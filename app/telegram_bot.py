#!/usr/bin/env python3
"""
Telegram Bot para receber arquivos HTML e iniciar pipeline de processamento
Sistema de produção com filas (pendentes → enviados) e logs por data
"""
import os
import json
import logging
import asyncio
from datetime import datetime, time
from pathlib import Path
from typing import Optional, Dict, Tuple

from dotenv import load_dotenv
import requests
from telegram import Update, Document
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Importar módulos do projeto
from .post_processor import PostProcessor
from .html_parser import HTMLParser, validate_html_file
from .linkedin_poster import observability, logger
from .content_reviewer import ContentReviewer  # 🆕 Revisor de conteúdo

# Carregar configurações
load_dotenv()

# Configurações do bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Sistema de filas em produção
POSTS_BASE_DIR = "posts"
POSTS_PENDENTES_DIR = os.path.join(POSTS_BASE_DIR, "pendentes")
POSTS_ENVIADOS_DIR = os.path.join(POSTS_BASE_DIR, "enviados")
POSTS_LOGS_DIR = os.path.join(POSTS_BASE_DIR, "logs")

# Configurar diretórios de produção
for directory in [
    POSTS_BASE_DIR,
    POSTS_PENDENTES_DIR,
    POSTS_ENVIADOS_DIR,
    POSTS_LOGS_DIR,
]:
    os.makedirs(directory, exist_ok=True)


class TelegramPipeline:
    """Gerenciador do pipeline Telegram → GPT → Revisão → LinkedIn com sistema de filas de produção"""

    def __init__(self):
        self.processor = PostProcessor()
        self.html_parser = HTMLParser()
        self.reviewer = ContentReviewer()  # 🆕 Revisor
        self.authorized_users = self._get_authorized_users()
        self.setup_daily_logger()

        # 🆕 Sistema de aprovação temporária
        self.pending_approvals = (
            {}
        )  # {user_id: {content, file_path, execution_id, etc}}

    def setup_daily_logger(self):
        """Configurar logger por data (YYYY-MM-DD.log)"""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(POSTS_LOGS_DIR, f"{today}.log")

        # Configurar handler específico para o pipeline
        self.pipeline_logger = logging.getLogger(f"pipeline_{today}")
        self.pipeline_logger.setLevel(logging.INFO)

        # Evitar duplicação de handlers
        if not self.pipeline_logger.handlers:
            handler = logging.FileHandler(log_file, encoding="utf-8")
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.pipeline_logger.addHandler(handler)

        self.pipeline_logger.info(f"📅 Pipeline iniciado - {today}")

    def _get_authorized_users(self) -> list:
        """Obter lista de usuários autorizados"""
        authorized = os.getenv("TELEGRAM_AUTHORIZED_USERS", "")
        if authorized:
            return [int(uid.strip()) for uid in authorized.split(",")]
        return []

    def is_authorized(self, user_id: int) -> bool:
        """Verificar se usuário está autorizado"""
        if not self.authorized_users:
            return True  # Se não configurado, permite todos
        return user_id in self.authorized_users

    def validate_posting_time(self) -> Dict:
        """Validar se é um horário apropriado para posting"""
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()  # 0=segunda, 6=domingo

        validation = {"valid": True, "warnings": [], "recommendations": []}

        # Horários recomendados para LinkedIn (8h-18h dias úteis)
        business_start = time(8, 0)  # 08:00
        business_end = time(18, 0)  # 18:00

        # Verificar se é dia útil (segunda a sexta)
        if current_day >= 5:  # sábado ou domingo
            validation["warnings"].append(
                f"📅 Final de semana - menor engajamento esperado"
            )
            validation["recommendations"].append(
                "Considere agendar para segunda-feira 8h-10h"
            )

        # Verificar horário
        if current_time < business_start:
            validation["warnings"].append(
                f"🕐 Muito cedo ({now.strftime('%H:%M')}) - audiência ainda não ativa"
            )
            validation["recommendations"].append("Horário ideal: 8h-10h ou 17h-19h")
        elif current_time > business_end:
            validation["warnings"].append(
                f"🕐 Horário tardio ({now.strftime('%H:%M')}) - menor visibilidade"
            )
            validation["recommendations"].append(
                "Considere postar entre 8h-18h nos dias úteis"
            )
        else:
            validation["recommendations"].append(
                f"✅ Bom horário para posting ({now.strftime('%H:%M')})"
            )

        return validation

    def create_standardized_filename(
        self, document: Document, metadata: Dict
    ) -> Tuple[str, str]:
        """Criar nome de arquivo padronizado na fila de pendentes"""

        # Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Slug do título
        title = metadata.get("title", "")
        if not title and document.file_name:
            # Usar nome do arquivo original como fallback
            title = Path(document.file_name).stem

        slug = self.html_parser.create_slug(title) if title else "sem_titulo"

        # Nome final padronizado na fila de pendentes
        filename = f"{timestamp}_{slug}.html"
        filepath = os.path.join(POSTS_PENDENTES_DIR, filename)

        # Garantir que não existe conflito
        counter = 1
        while os.path.exists(filepath):
            filename = f"{timestamp}_{slug}_{counter}.html"
            filepath = os.path.join(POSTS_PENDENTES_DIR, filename)
            counter += 1

        return filepath, filename

    def save_metadata(
        self, filepath: str, metadata: Dict, document: Document, user_id: int
    ) -> str:
        """Salvar metadata.json junto com o arquivo HTML"""

        # Criar metadata expandido
        full_metadata = {
            **metadata,
            "telegram": {
                "user_id": user_id,
                "file_name": document.file_name,
                "file_size": document.file_size,
                "mime_type": document.mime_type,
                "received_at": datetime.now().isoformat(),
            },
            "processing": {
                "status": "pendente",
                "queue": "pendentes",
                "pipeline_id": None,
                "processed_at": None,
                "published_at": None,
                "moved_to_enviados_at": None,
            },
            "validation": {
                "html_valid": metadata.get("valid", False),
                "time_check": self.validate_posting_time(),
            },
            "production": {
                "daily_log": datetime.now().strftime("%Y-%m-%d.log"),
                "queue_position": self.get_queue_position(),
            },
        }

        # Caminho do metadata
        metadata_path = filepath.replace(".html", ".metadata.json")

        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(full_metadata, f, indent=2, ensure_ascii=False)

            self.pipeline_logger.info(
                f"📋 Metadata salvo: {os.path.basename(metadata_path)}"
            )
            return metadata_path

        except Exception as e:
            self.pipeline_logger.error(f"❌ Erro ao salvar metadata: {e}")
            return ""

    def get_queue_position(self) -> int:
        """Obter posição atual na fila de pendentes"""
        try:
            files = [f for f in os.listdir(POSTS_PENDENTES_DIR) if f.endswith(".html")]
            return len(files) + 1
        except:
            return 1

    def move_to_enviados(
        self, pendente_path: str, metadata_path: str
    ) -> Tuple[str, str]:
        """Mover arquivo processado de pendentes para enviados"""
        try:
            filename = os.path.basename(pendente_path)
            metadata_filename = os.path.basename(metadata_path)

            # Caminhos de destino
            enviado_path = os.path.join(POSTS_ENVIADOS_DIR, filename)
            enviado_metadata_path = os.path.join(POSTS_ENVIADOS_DIR, metadata_filename)

            # Mover arquivos
            os.rename(pendente_path, enviado_path)

            # Atualizar metadata antes de mover
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    meta = json.load(f)
                meta["processing"]["status"] = "enviado"
                meta["processing"]["queue"] = "enviados"
                meta["processing"]["moved_to_enviados_at"] = datetime.now().isoformat()

                with open(metadata_path, "w") as f:
                    json.dump(meta, f, indent=2)

                os.rename(metadata_path, enviado_metadata_path)

            self.pipeline_logger.info(f"📤 Movido para enviados: {filename}")
            return enviado_path, enviado_metadata_path

        except Exception as e:
            self.pipeline_logger.error(f"❌ Erro ao mover para enviados: {e}")
            return pendente_path, metadata_path

    async def download_and_validate_file(
        self, document: Document, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ) -> Optional[Dict]:
        """Baixar arquivo e fazer validação completa na fila de pendentes"""
        try:
            # 1. Baixar arquivo temporário primeiro
            temp_path = f"{POSTS_PENDENTES_DIR}/temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

            file = await document.get_file()
            await file.download_to_drive(temp_path)

            self.pipeline_logger.info(
                f"📥 Arquivo temporário baixado: {os.path.basename(temp_path)}"
            )

            # 2. Validar conteúdo HTML
            validation = validate_html_file(temp_path)

            if not validation["valid"]:
                # Remover arquivo temporário se inválido
                os.remove(temp_path)
                self.pipeline_logger.warning(
                    f"❌ Arquivo inválido removido: {document.file_name}"
                )
                return {"status": "invalid", "validation": validation}

            # 3. Extrair metadados
            metadata = self.html_parser.extract_metadata(temp_path)
            metadata.update(validation)  # Incluir dados de validação

            # 4. Criar nome de arquivo padronizado na fila
            final_path, filename = self.create_standardized_filename(document, metadata)

            # 5. Mover arquivo para nome final na fila de pendentes
            os.rename(temp_path, final_path)

            # 6. Salvar metadata.json
            metadata_path = self.save_metadata(final_path, metadata, document, user_id)

            queue_position = (
                self.get_queue_position() - 1
            )  # -1 porque já foi adicionado
            self.pipeline_logger.info(
                f"✅ Arquivo na fila: {filename} (posição {queue_position})"
            )

            return {
                "status": "success",
                "file_path": final_path,
                "filename": filename,
                "metadata_path": metadata_path,
                "metadata": metadata,
                "validation": validation,
                "queue_position": queue_position,
            }

        except Exception as e:
            # Limpar arquivo temporário se existir
            if "temp_path" in locals() and os.path.exists(temp_path):
                os.remove(temp_path)

            self.pipeline_logger.error(f"❌ Erro ao processar arquivo: {e}")
            return {"status": "error", "error": str(e)}

    async def process_pipeline_with_review(
        self, file_path: str, user_id: int, metadata: Dict
    ) -> dict:
        """Executar pipeline com revisão pré-publicação"""
        execution_id = f"tg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        start_time = datetime.now()

        try:
            # Log início do pipeline
            self.pipeline_logger.info(
                f"🚀 Pipeline com revisão iniciado: {execution_id}"
            )

            # 1. Atualizar metadata de status
            metadata_path = file_path.replace(".html", ".metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    meta = json.load(f)
                meta["processing"]["status"] = "processando"
                meta["processing"]["pipeline_id"] = execution_id
                with open(metadata_path, "w") as f:
                    json.dump(meta, f, indent=2)

            # 2. Processar com GPT
            self.pipeline_logger.info("🤖 Processando conteúdo com GPT-4o-mini...")
            processed_content = await self.processor.process_html_file(file_path)

            if not processed_content:
                raise Exception("Falha no processamento GPT")

            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self.pipeline_logger.info(f"✅ GPT processado em {processing_time}ms")

            # 3. 🆕 REVISÃO PRÉ-PUBLICAÇÃO
            self.pipeline_logger.info("📋 Iniciando revisão de conteúdo...")
            review = self.reviewer.review_content(
                processed_content, metadata.get("title", "")
            )

            # Salvar review
            review_path = self.reviewer.save_review(review, file_path)
            self.pipeline_logger.info(f"📋 Review salvo: {review_path}")

            # Atualizar metadata com review
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    meta = json.load(f)
                meta["processing"]["status"] = "aguardando_aprovacao"
                meta["content_review"] = review
                meta["review_path"] = review_path
                with open(metadata_path, "w") as f:
                    json.dump(meta, f, indent=2)

            # 4. Armazenar para aprovação
            self.pending_approvals[user_id] = {
                "execution_id": execution_id,
                "file_path": file_path,
                "metadata_path": metadata_path,
                "processed_content": processed_content,
                "review": review,
                "original_metadata": metadata,
                "created_at": datetime.now().isoformat(),
            }

            review_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self.pipeline_logger.info(
                f"📋 Revisão completa em {review_time}ms - Aguardando aprovação"
            )

            return {
                "status": "awaiting_approval",
                "execution_id": execution_id,
                "processed_content": processed_content,
                "review": review,
                "duration_ms": review_time,
                "title": metadata.get("title", "N/A"),
                "requires_approval": True,
            }

        except Exception as e:
            # Log erro no pipeline
            error_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self.pipeline_logger.error(
                f"💥 Erro no pipeline com revisão {execution_id}: {e}"
            )

            # Atualizar metadata com erro
            metadata_path = file_path.replace(".html", ".metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    meta = json.load(f)
                meta["processing"]["status"] = "erro"
                meta["processing"]["error"] = str(e)
                meta["processing"]["error_at"] = datetime.now().isoformat()
                with open(metadata_path, "w") as f:
                    json.dump(meta, f, indent=2)

            return {
                "status": "error",
                "execution_id": execution_id,
                "error": str(e),
                "duration_ms": error_time,
            }

    async def publish_approved_content(self, user_id: int) -> dict:
        """Publicar conteúdo aprovado pelo usuário"""
        if user_id not in self.pending_approvals:
            return {"status": "error", "error": "Nenhum conteúdo aguardando aprovação"}

        approval_data = self.pending_approvals[user_id]
        execution_id = approval_data["execution_id"]
        processed_content = approval_data["processed_content"]
        file_path = approval_data["file_path"]
        metadata_path = approval_data["metadata_path"]

        start_time = datetime.now()

        try:
            # Atualizar status para publicando
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    meta = json.load(f)
                meta["processing"]["status"] = "publicando"
                meta["processing"]["approved_at"] = start_time.isoformat()
                with open(metadata_path, "w") as f:
                    json.dump(meta, f, indent=2)

            # Publicar no LinkedIn
            self.pipeline_logger.info(
                f"🔗 Publicando conteúdo aprovado: {execution_id}"
            )
            from .linkedin_poster import get_driver, login, publish_post

            driver = None
            try:
                driver = get_driver()
                login(driver, execution_id)
                publish_post(driver, processed_content, execution_id)

                # Mover para enviados após sucesso
                enviado_path, enviado_metadata_path = self.move_to_enviados(
                    file_path, metadata_path
                )

                # Atualizar metadata final
                if os.path.exists(enviado_metadata_path):
                    with open(enviado_metadata_path, "r") as f:
                        meta = json.load(f)
                    meta["processing"]["status"] = "publicado"
                    meta["processing"]["published_at"] = datetime.now().isoformat()
                    meta["processing"]["final_content"] = processed_content
                    with open(enviado_metadata_path, "w") as f:
                        json.dump(meta, f, indent=2)

                # Limpar aprovação pendente
                del self.pending_approvals[user_id]

                total_time = int((datetime.now() - start_time).total_seconds() * 1000)
                self.pipeline_logger.info(
                    f"🎉 Publicação aprovada completa: {execution_id} em {total_time}ms"
                )

                return {
                    "status": "published",
                    "execution_id": execution_id,
                    "processed_content": processed_content,
                    "duration_ms": total_time,
                    "moved_to": "enviados",
                }

            finally:
                if driver:
                    driver.quit()

        except Exception as e:
            error_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self.pipeline_logger.error(
                f"💥 Erro na publicação aprovada {execution_id}: {e}"
            )

            # Manter em pendentes com erro, mas não remover da aprovação
            # O usuário pode tentar novamente
            return {
                "status": "error",
                "execution_id": execution_id,
                "error": str(e),
                "duration_ms": error_time,
            }


# Instância global do pipeline
pipeline = TelegramPipeline()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
        return

    # Verificar horário atual
    time_check = pipeline.validate_posting_time()
    time_info = ""
    if time_check["warnings"]:
        time_info = f"\n⚠️ {time_check['warnings'][0]}"
    if time_check["recommendations"]:
        time_info += f"\n💡 {time_check['recommendations'][0]}"

    # Status da fila
    pendentes = len([f for f in os.listdir(POSTS_PENDENTES_DIR) if f.endswith(".html")])
    enviados = len([f for f in os.listdir(POSTS_ENVIADOS_DIR) if f.endswith(".html")])

    # Verificar se tem aprovação pendente
    approval_status = ""
    if user_id in pipeline.pending_approvals:
        approval_status = (
            "\n🔔 **VOCÊ TEM CONTEÚDO AGUARDANDO APROVAÇÃO** - Use /pending"
        )

    message = f"""
🚀 **LinkedIn Content Pipeline Bot v2.6.1**

Envie um arquivo HTML e eu vou:
1. 📥 Adicionar à fila de **pendentes**
2. 📋 Extrair metadados (título, descrição, etc.)
3. 🤖 Processar com GPT-4o-mini
4. 📋 **REVISAR CONTEÚDO** (sem alterar estilo)
5. ⏸️ **AGUARDAR SUA APROVAÇÃO**
6. 🔗 Publicar no LinkedIn (após aprovação)
7. 📤 Mover para **enviados**
8. 💾 Log diário: `{datetime.now().strftime('%Y-%m-%d.log')}`

**Sistema de Filas de Produção:**
📂 Pendentes: {pendentes} arquivos
📤 Enviados: {enviados} arquivos
{approval_status}

**🔍 Sistema de Revisão:**
✅ Validação de gramática/ortografia
✅ Verificação de compliance LinkedIn
✅ Análise de tom profissional
✅ **Aprovação manual obrigatória**

**📱 Comandos principais:**
/start - Mostrar esta mensagem
/queue - Status da fila
/status - Ver status do sistema
/stats - Estatísticas de uso

**📋 Comandos de aprovação:**
/pending - Ver conteúdo aguardando aprovação
/approve - Aprovar e publicar
/cancel - Cancelar conteúdo
/retry - Tentar publicar novamente

**Validações automáticas:**
✅ Conteúdo HTML válido
✅ Tamanho adequado (50+ chars)
✅ Estrutura de arquivo padronizada
✅ Horário de posting otimizado
{time_info}
"""

    await update.message.reply_text(message, parse_mode="Markdown")


async def queue_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /queue - Status da fila de produção"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
        return

    try:
        # Analisar fila de pendentes
        pendentes_files = [
            f for f in os.listdir(POSTS_PENDENTES_DIR) if f.endswith(".html")
        ]
        enviados_files = [
            f for f in os.listdir(POSTS_ENVIADOS_DIR) if f.endswith(".html")
        ]

        # Próximos 3 na fila
        next_in_queue = sorted(pendentes_files)[:3]

        # Últimos 3 enviados
        last_sent = sorted(enviados_files, reverse=True)[:3]

        queue_msg = f"""
📊 **Status da Fila de Produção:**

📂 **Pendentes: {len(pendentes_files)} arquivos**
"""

        if next_in_queue:
            queue_msg += "\n🔄 **Próximos na fila:**\n"
            for i, file in enumerate(next_in_queue, 1):
                timestamp = file.split("_")[0]
                title = file.split("_", 1)[1].replace(".html", "").replace("-", " ")
                queue_msg += f"{i}. `{timestamp}` - {title[:30]}...\n"
        else:
            queue_msg += "\n✅ Fila vazia\n"

        queue_msg += f"\n📤 **Enviados: {len(enviados_files)} arquivos**"

        if last_sent:
            queue_msg += "\n🎉 **Últimos enviados:**\n"
            for file in last_sent:
                timestamp = file.split("_")[0]
                title = file.split("_", 1)[1].replace(".html", "").replace("-", " ")
                queue_msg += f"• `{timestamp}` - {title[:30]}...\n"

        # Log atual
        today_log = datetime.now().strftime("%Y-%m-%d.log")
        queue_msg += f"\n📝 **Log atual:** `{today_log}`"

        await update.message.reply_text(queue_msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao verificar fila: {e}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /status com validações expandidas"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
        return

    # Verificar status dos componentes
    status_msg = "📊 **Status do Sistema v2.6.0:**\n\n"

    # Verificar OpenAI
    if os.getenv("OPENAI_API_KEY"):
        status_msg += "✅ OpenAI API configurada\n"
    else:
        status_msg += "❌ OpenAI API não configurada\n"

    # Verificar LinkedIn
    if os.getenv("LINKEDIN_EMAIL") and os.getenv("LINKEDIN_PASSWORD"):
        status_msg += "✅ LinkedIn configurado\n"
    else:
        status_msg += "❌ LinkedIn não configurado\n"

    # Verificar diretórios de produção
    pendentes = len([f for f in os.listdir(POSTS_PENDENTES_DIR) if f.endswith(".html")])
    enviados = len([f for f in os.listdir(POSTS_ENVIADOS_DIR) if f.endswith(".html")])
    logs_count = len([f for f in os.listdir(POSTS_LOGS_DIR) if f.endswith(".log")])

    status_msg += f"📂 Pendentes: {pendentes}\n"
    status_msg += f"📤 Enviados: {enviados}\n"
    status_msg += f"📝 Logs diários: {logs_count}\n"

    # Verificar horário atual
    time_check = pipeline.validate_posting_time()
    if time_check["warnings"]:
        status_msg += f"⚠️ {time_check['warnings'][0]}\n"
    if time_check["recommendations"]:
        status_msg += f"💡 {time_check['recommendations'][0]}\n"

    await update.message.reply_text(status_msg, parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /stats - Estatísticas avançadas com metadata"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
        return

    try:
        # Analisar arquivos metadata nas duas filas
        pendentes_metadata = [
            f for f in os.listdir(POSTS_PENDENTES_DIR) if f.endswith(".metadata.json")
        ]
        enviados_metadata = [
            f for f in os.listdir(POSTS_ENVIADOS_DIR) if f.endswith(".metadata.json")
        ]

        published_count = 0
        error_count = 0
        processing_count = 0
        pendente_count = 0

        # Analisar pendentes
        for meta_file in pendentes_metadata:
            try:
                with open(os.path.join(POSTS_PENDENTES_DIR, meta_file), "r") as f:
                    meta = json.load(f)

                status = meta.get("processing", {}).get("status", "unknown")
                if status == "pendente":
                    pendente_count += 1
                elif status == "processando":
                    processing_count += 1
                elif status == "erro":
                    error_count += 1
            except:
                continue

        # Analisar enviados
        for meta_file in enviados_metadata:
            try:
                with open(os.path.join(POSTS_ENVIADOS_DIR, meta_file), "r") as f:
                    meta = json.load(f)

                status = meta.get("processing", {}).get("status", "unknown")
                if status in ["publicado", "enviado"]:
                    published_count += 1
            except:
                continue

        # Ler estatísticas do CSV se existir
        csv_stats = ""
        csv_file = observability.csv_log_file
        if os.path.exists(csv_file):
            with open(csv_file, "r") as f:
                lines = f.readlines()

            total_records = len(lines) - 1  # -1 para header
            telegram_pipelines = len([l for l in lines if "telegram_start" in l])
            successes = len([l for l in lines if ",True," in l])
            failures = len([l for l in lines if ",False," in l])
            success_rate = (
                (successes * 100) // total_records if total_records > 0 else 0
            )

            csv_stats = f"""
📈 **CSV Audit:**
• Total registros: {total_records}
• Pipelines Telegram: {telegram_pipelines}
• Sucessos: {successes}
• Falhas: {failures}
• Taxa de sucesso: {success_rate}%
"""

        stats_msg = f"""
📊 **Estatísticas Avançadas v2.6.0:**
{csv_stats}
📋 **Sistema de Filas:**
• 📂 Pendentes: {pendente_count}
• 🔄 Processando: {processing_count}
• 📤 Publicados: {published_count}
• ❌ Erros: {error_count}

📝 **Logs por Data:**
• Log atual: `{datetime.now().strftime('%Y-%m-%d.log')}`
• Total logs: {len([f for f in os.listdir(POSTS_LOGS_DIR) if f.endswith('.log')])}

⏰ **Horário atual:** {datetime.now().strftime('%H:%M - %A')}

Para detalhes completos:
`./monitor_logs.sh`
"""

        await update.message.reply_text(stats_msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao obter estatísticas: {e}")


async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /approve - Aprovar conteúdo para publicação"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
        return

    if user_id not in pipeline.pending_approvals:
        await update.message.reply_text("❌ Nenhum conteúdo aguardando aprovação")
        return

    processing_msg = await update.message.reply_text(
        "✅ Aprovado! Publicando no LinkedIn..."
    )

    try:
        # Publicar conteúdo aprovado
        result = await pipeline.publish_approved_content(user_id)

        if result["status"] == "published":
            success_msg = f"""
✅ **PUBLICADO COM SUCESSO!**

🆔 **ID:** `{result["execution_id"]}`
⏱️ **Tempo:** {result["duration_ms"]}ms
📤 **Status:** Movido para enviados
🔗 **LinkedIn:** Post publicado!

📝 **Log:** `{datetime.now().strftime('%Y-%m-%d.log')}`
"""
            await processing_msg.edit_text(success_msg, parse_mode="Markdown")
        else:
            error_msg = f"""
❌ **Erro na publicação**

🆔 **ID:** `{result["execution_id"]}`
🚨 **Erro:** {result["error"]}
⏱️ **Tempo:** {result["duration_ms"]}ms

O conteúdo permanece aguardando aprovação.
Use /retry para tentar novamente.
"""
            await processing_msg.edit_text(error_msg, parse_mode="Markdown")

    except Exception as e:
        await processing_msg.edit_text(f"❌ Erro inesperado na aprovação: {e}")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /cancel - Cancelar conteúdo pendente"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
        return

    if user_id not in pipeline.pending_approvals:
        await update.message.reply_text("❌ Nenhum conteúdo aguardando aprovação")
        return

    # Pegar dados da aprovação
    approval_data = pipeline.pending_approvals[user_id]
    execution_id = approval_data["execution_id"]
    file_path = approval_data["file_path"]
    metadata_path = approval_data["metadata_path"]

    # Atualizar metadata como cancelado
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                meta = json.load(f)
            meta["processing"]["status"] = "cancelado"
            meta["processing"]["cancelled_at"] = datetime.now().isoformat()
            with open(metadata_path, "w") as f:
                json.dump(meta, f, indent=2)

        # Remover da lista de aprovações
        del pipeline.pending_approvals[user_id]

        # Log do cancelamento
        pipeline.pipeline_logger.info(
            f"🚫 Conteúdo cancelado pelo usuário: {execution_id}"
        )

        await update.message.reply_text(
            f"""
🚫 **Conteúdo cancelado**

🆔 **ID:** `{execution_id}`
📁 **Status:** Cancelado (mantido em pendentes)
📝 **Log:** `{datetime.now().strftime('%Y-%m-%d.log')}`

Você pode enviar um novo arquivo quando desejar.
""",
            parse_mode="Markdown",
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao cancelar: {e}")


async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /pending - Ver conteúdo aguardando aprovação"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
        return

    if user_id not in pipeline.pending_approvals:
        await update.message.reply_text("✅ Nenhum conteúdo aguardando aprovação")
        return

    # Mostrar conteúdo pendente
    approval_data = pipeline.pending_approvals[user_id]
    review = approval_data["review"]
    content = approval_data["processed_content"]

    # Formatar para Telegram
    review_message = pipeline.reviewer.format_review_for_telegram(review, content)

    await update.message.reply_text(review_message, parse_mode="Markdown")


async def retry_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /retry - Tentar publicar novamente"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
        return

    if user_id not in pipeline.pending_approvals:
        await update.message.reply_text("❌ Nenhum conteúdo aguardando aprovação")
        return

    processing_msg = await update.message.reply_text(
        "🔄 Tentando publicar novamente..."
    )

    try:
        result = await pipeline.publish_approved_content(user_id)

        if result["status"] == "published":
            success_msg = f"""
✅ **PUBLICADO COM SUCESSO!** (retry)

🆔 **ID:** `{result["execution_id"]}`
⏱️ **Tempo:** {result["duration_ms"]}ms
📤 **Status:** Movido para enviados
🔗 **LinkedIn:** Post publicado!
"""
            await processing_msg.edit_text(success_msg, parse_mode="Markdown")
        else:
            error_msg = f"""
❌ **Retry falhou**

🚨 **Erro:** {result["error"]}
⏱️ **Tempo:** {result["duration_ms"]}ms

Use /cancel para desistir ou /retry para tentar novamente.
"""
            await processing_msg.edit_text(error_msg, parse_mode="Markdown")

    except Exception as e:
        await processing_msg.edit_text(f"❌ Erro no retry: {e}")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processar arquivo recebido com sistema de filas e revisão"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
        return

    # Verificar se já tem conteúdo aguardando aprovação
    if user_id in pipeline.pending_approvals:
        await update.message.reply_text(
            """
⚠️ **Você tem conteúdo aguardando aprovação**

Use um destes comandos primeiro:
• /pending - Ver conteúdo aguardando
• /approve - Aprovar e publicar
• /cancel - Cancelar conteúdo atual

Depois envie o novo arquivo.
""",
            parse_mode="Markdown",
        )
        return

    document = update.message.document

    # Verificar se é arquivo HTML
    if not document.file_name or not document.file_name.lower().endswith(".html"):
        await update.message.reply_text(
            "❌ Por favor, envie apenas arquivos HTML (.html)"
        )
        return

    # Verificar tamanho do arquivo (limite: 10MB)
    if document.file_size > 10 * 1024 * 1024:  # 10MB
        await update.message.reply_text("❌ Arquivo muito grande. Máximo: 10MB")
        return

    # Enviar confirmação de recebimento
    processing_msg = await update.message.reply_text(
        f"📥 Recebido: `{document.file_name}`\n🔄 Adicionando à fila de pendentes..."
    )

    try:
        # 1. Baixar e validar arquivo (adiciona à fila de pendentes)
        result = await pipeline.download_and_validate_file(document, context, user_id)

        if result["status"] == "invalid":
            validation = result["validation"]
            error_msg = f"""
❌ **Arquivo inválido**

**Problemas encontrados:**
{chr(10).join([f"• {issue}" for issue in validation["issues"]])}

**Avisos:**
{chr(10).join([f"• {warning}" for warning in validation.get("warnings", [])])}

Por favor, envie um arquivo HTML válido.
"""
            await processing_msg.edit_text(error_msg, parse_mode="Markdown")
            return

        if result["status"] == "error":
            await processing_msg.edit_text(
                f"❌ Erro ao processar arquivo: {result['error']}"
            )
            return

        # 2. Mostrar status da fila
        metadata = result["metadata"]
        time_check = pipeline.validate_posting_time()

        queue_msg = f"""
✅ **Arquivo adicionado à fila!**

📂 **Arquivo:** `{result['filename']}`
📝 **Título:** {metadata.get('title', 'N/A')}
📊 **Palavras:** {metadata.get('word_count', 0)}
📏 **Caracteres:** {metadata.get('char_count', 0)}
🏷️ **Posição na fila:** {result.get('queue_position', 'N/A')}

📂 **Status:** PENDENTE ➜ processando ➜ enviados
"""

        if time_check["warnings"]:
            queue_msg += f"\n⚠️ {time_check['warnings'][0]}"
        if time_check["recommendations"]:
            queue_msg += f"\n💡 {time_check['recommendations'][0]}"

        queue_msg += "\n\n🤖 Iniciando processamento com revisão..."

        await processing_msg.edit_text(queue_msg, parse_mode="Markdown")

        # 3. Executar pipeline com revisão
        pipeline_result = await pipeline.process_pipeline_with_review(
            result["file_path"], user_id, metadata
        )

        if pipeline_result["status"] == "awaiting_approval":
            review = pipeline_result["review"]

            # Formatar review para Telegram
            review_message = pipeline.reviewer.format_review_for_telegram(
                review, pipeline_result["processed_content"]
            )

            final_msg = f"""
✅ **Processamento completo - AGUARDANDO APROVAÇÃO**

🆔 **ID:** `{pipeline_result["execution_id"]}`
⏱️ **Tempo:** {pipeline_result["duration_ms"]}ms
📁 **Status:** pendentes → aguardando aprovação

{review_message}
"""
            await processing_msg.edit_text(final_msg, parse_mode="Markdown")

        else:
            error_msg = f"""
❌ **Erro no pipeline**

🆔 **ID:** `{pipeline_result["execution_id"]}`
⏱️ **Tempo:** {pipeline_result["duration_ms"]}ms
🚨 **Erro:** {pipeline_result["error"]}

📁 **Status:** Mantido em **pendentes** para retry
"""
            await processing_msg.edit_text(error_msg, parse_mode="Markdown")

    except Exception as e:
        pipeline.pipeline_logger.error(f"❌ Erro no handler de documento: {e}")
        await processing_msg.edit_text(f"❌ Erro inesperado: {e}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processar mensagem de texto"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        return

    await update.message.reply_text(
        "📄 Por favor, envie um arquivo HTML para adicionar à fila.\n"
        "Use /queue para ver o status da fila ou /start para instruções."
    )


def main():
    """Função principal do bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN não configurado")
        return

    logger.info("🚀 Iniciando Telegram Bot v2.6.1 com Revisão de Conteúdo...")

    # Criar aplicação
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrar handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("queue", queue_command))
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("pending", pending_command))
    application.add_handler(CommandHandler("retry", retry_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    logger.info("✅ Telegram Bot v2.6.1 iniciado com Sistema de Revisão")
    logger.info(
        "📋 Comandos de aprovação disponíveis: /approve, /cancel, /pending, /retry"
    )

    # Executar bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

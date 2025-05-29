#!/usr/bin/env python3
"""
Telegram Bot para receber arquivos HTML e iniciar pipeline de processamento
Sistema completo com validações, metadata.json e arquivos padronizados
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

# Carregar configurações
load_dotenv()

# Configurações do bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
POSTS_DIR = "posts"

# Configurar diretório de posts
os.makedirs(POSTS_DIR, exist_ok=True)


class TelegramPipeline:
    """Gerenciador do pipeline Telegram → GPT → LinkedIn com validações avançadas"""

    def __init__(self):
        self.processor = PostProcessor()
        self.html_parser = HTMLParser()
        self.authorized_users = self._get_authorized_users()

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
        """Criar nome de arquivo padronizado: timestamp_slug-titulo.html"""

        # Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Slug do título
        title = metadata.get("title", "")
        if not title and document.file_name:
            # Usar nome do arquivo original como fallback
            title = Path(document.file_name).stem

        slug = self.html_parser.create_slug(title) if title else "sem_titulo"

        # Nome final padronizado
        filename = f"{timestamp}_{slug}.html"
        filepath = os.path.join(POSTS_DIR, filename)

        # Garantir que não existe conflito
        counter = 1
        while os.path.exists(filepath):
            filename = f"{timestamp}_{slug}_{counter}.html"
            filepath = os.path.join(POSTS_DIR, filename)
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
                "status": "received",
                "pipeline_id": None,
                "processed_at": None,
                "published_at": None,
            },
            "validation": {
                "html_valid": metadata.get("valid", False),
                "time_check": self.validate_posting_time(),
            },
        }

        # Caminho do metadata
        metadata_path = filepath.replace(".html", ".metadata.json")

        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(full_metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"📋 Metadata salvo: {metadata_path}")
            return metadata_path

        except Exception as e:
            logger.error(f"❌ Erro ao salvar metadata: {e}")
            return ""

    async def download_and_validate_file(
        self, document: Document, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ) -> Optional[Dict]:
        """Baixar arquivo e fazer validação completa"""
        try:
            # 1. Baixar arquivo temporário primeiro
            temp_path = (
                f"{POSTS_DIR}/temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )

            file = await document.get_file()
            await file.download_to_drive(temp_path)

            logger.info(f"📥 Arquivo temporário baixado: {temp_path}")

            # 2. Validar conteúdo HTML
            validation = validate_html_file(temp_path)

            if not validation["valid"]:
                # Remover arquivo temporário se inválido
                os.remove(temp_path)
                return {"status": "invalid", "validation": validation}

            # 3. Extrair metadados
            metadata = self.html_parser.extract_metadata(temp_path)
            metadata.update(validation)  # Incluir dados de validação

            # 4. Criar nome de arquivo padronizado
            final_path, filename = self.create_standardized_filename(document, metadata)

            # 5. Mover arquivo para nome final
            os.rename(temp_path, final_path)

            # 6. Salvar metadata.json
            metadata_path = self.save_metadata(final_path, metadata, document, user_id)

            logger.info(f"✅ Arquivo processado: {filename}")

            return {
                "status": "success",
                "file_path": final_path,
                "filename": filename,
                "metadata_path": metadata_path,
                "metadata": metadata,
                "validation": validation,
            }

        except Exception as e:
            # Limpar arquivo temporário se existir
            if "temp_path" in locals() and os.path.exists(temp_path):
                os.remove(temp_path)

            logger.error(f"❌ Erro ao processar arquivo: {e}")
            return {"status": "error", "error": str(e)}

    async def process_pipeline(
        self, file_path: str, user_id: int, metadata: Dict
    ) -> dict:
        """Executar pipeline completo com metadata tracking"""
        execution_id = f"tg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        start_time = datetime.now()

        try:
            # Log início do pipeline
            observability.log_csv_event(
                execution_id,
                "telegram_start",
                True,
                "",
                f"file://{file_path}",
                "",
                "",
                "",
                0,
            )

            # 1. Atualizar metadata de status
            metadata_path = file_path.replace(".html", ".metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    meta = json.load(f)
                meta["processing"]["status"] = "processing"
                meta["processing"]["pipeline_id"] = execution_id
                with open(metadata_path, "w") as f:
                    json.dump(meta, f, indent=2)

            # 2. Processar com GPT
            logger.info("🤖 Processando conteúdo com GPT-4o-mini...")
            processed_content = await self.processor.process_html_file(file_path)

            if not processed_content:
                raise Exception("Falha no processamento GPT")

            # Log processamento GPT
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            observability.log_csv_event(
                execution_id,
                "gpt_processing",
                True,
                processed_content[:100],
                f"file://{file_path}",
                "",
                "",
                "",
                processing_time,
            )

            # 3. Publicar no LinkedIn
            logger.info("🔗 Publicando no LinkedIn...")
            from .linkedin_poster import get_driver, login, publish_post

            driver = None
            try:
                driver = get_driver()
                login(driver, execution_id)
                publish_post(driver, processed_content, execution_id)

                # 4. Atualizar metadata final
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as f:
                        meta = json.load(f)
                    meta["processing"]["status"] = "published"
                    meta["processing"]["processed_at"] = datetime.now().isoformat()
                    meta["processing"]["published_at"] = datetime.now().isoformat()
                    meta["processing"]["final_content"] = processed_content
                    with open(metadata_path, "w") as f:
                        json.dump(meta, f, indent=2)

                # Log sucesso total
                total_time = int((datetime.now() - start_time).total_seconds() * 1000)
                observability.log_csv_event(
                    execution_id,
                    "pipeline_complete",
                    True,
                    processed_content,
                    "https://linkedin.com/feed/",
                    "",
                    "",
                    "",
                    total_time,
                )

                return {
                    "status": "success",
                    "execution_id": execution_id,
                    "processed_content": processed_content,
                    "duration_ms": total_time,
                    "title": metadata.get("title", "N/A"),
                    "word_count": metadata.get("word_count", 0),
                }

            finally:
                if driver:
                    driver.quit()

        except Exception as e:
            # Log erro no pipeline
            error_time = int((datetime.now() - start_time).total_seconds() * 1000)
            observability.log_csv_event(
                execution_id,
                "pipeline_error",
                False,
                "",
                f"file://{file_path}",
                type(e).__name__,
                str(e),
                "",
                error_time,
            )

            # Atualizar metadata com erro
            metadata_path = file_path.replace(".html", ".metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    meta = json.load(f)
                meta["processing"]["status"] = "error"
                meta["processing"]["error"] = str(e)
                meta["processing"]["error_at"] = datetime.now().isoformat()
                with open(metadata_path, "w") as f:
                    json.dump(meta, f, indent=2)

            # Enviar alerta
            observability.send_alert(
                "Erro no Pipeline Telegram", str(e), f"file://{file_path}"
            )

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

    message = f"""
🚀 **LinkedIn Content Pipeline Bot v2.5.1**

Envie um arquivo HTML e eu vou:
1. 📥 Baixar e validar o arquivo
2. 📋 Extrair metadados (título, descrição, etc.)
3. 🤖 Processar com GPT-4o-mini
4. 🔗 Publicar no LinkedIn
5. 💾 Salvar metadata.json completo

**Validações automáticas:**
✅ Conteúdo HTML válido
✅ Tamanho adequado (50+ chars)
✅ Estrutura de arquivo padronizada
✅ Horário de posting otimizado

**Arquivos salvos:**
📁 `YYYYMMDD_HHMMSS_slug-titulo.html`
📋 `YYYYMMDD_HHMMSS_slug-titulo.metadata.json`

**Comandos:**
/start - Mostrar esta mensagem
/status - Ver status do sistema  
/stats - Estatísticas de uso
{time_info}
"""

    await update.message.reply_text(message, parse_mode="Markdown")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /status com validações expandidas"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
        return

    # Verificar status dos componentes
    status_msg = "📊 **Status do Sistema v2.5.1:**\n\n"

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

    # Verificar diretório posts
    html_files = len([f for f in os.listdir(POSTS_DIR) if f.endswith(".html")])
    json_files = len([f for f in os.listdir(POSTS_DIR) if f.endswith(".metadata.json")])
    status_msg += f"📁 Arquivos HTML: {html_files}\n"
    status_msg += f"📋 Arquivos metadata: {json_files}\n"

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
        # Ler estatísticas do CSV
        csv_file = observability.csv_log_file

        if not os.path.exists(csv_file):
            await update.message.reply_text("📊 Nenhuma estatística disponível ainda")
            return

        # Analisar arquivos metadata
        metadata_files = [
            f for f in os.listdir(POSTS_DIR) if f.endswith(".metadata.json")
        ]

        published_count = 0
        error_count = 0
        processing_count = 0

        for meta_file in metadata_files:
            try:
                with open(os.path.join(POSTS_DIR, meta_file), "r") as f:
                    meta = json.load(f)

                status = meta.get("processing", {}).get("status", "unknown")
                if status == "published":
                    published_count += 1
                elif status == "error":
                    error_count += 1
                elif status == "processing":
                    processing_count += 1
            except:
                continue

        # Contar registros CSV
        with open(csv_file, "r") as f:
            lines = f.readlines()

        total_records = len(lines) - 1  # -1 para header
        telegram_pipelines = len([l for l in lines if "telegram_start" in l])
        successes = len([l for l in lines if ",True," in l])
        failures = len([l for l in lines if ",False," in l])

        success_rate = (successes * 100) // total_records if total_records > 0 else 0

        stats_msg = f"""
📊 **Estatísticas Avançadas v2.5.1:**

📈 **CSV Audit:**
• Total registros: {total_records}
• Pipelines Telegram: {telegram_pipelines}
• Sucessos: {successes}
• Falhas: {failures}
• Taxa de sucesso: {success_rate}%

📋 **Metadata Tracking:**
• Arquivos recebidos: {len(metadata_files)}
• Publicados com sucesso: {published_count}
• Erros de processamento: {error_count}
• Em processamento: {processing_count}

⏰ **Horário atual:** {datetime.now().strftime('%H:%M - %A')}

Para detalhes completos:
`./monitor_logs.sh`
"""

        await update.message.reply_text(stats_msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao obter estatísticas: {e}")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processar arquivo recebido com validações completas"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
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
        f"📥 Recebido: `{document.file_name}`\n🔄 Validando e processando..."
    )

    try:
        # 1. Baixar e validar arquivo
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

        # 2. Mostrar validações de horário
        metadata = result["metadata"]
        time_check = pipeline.validate_posting_time()

        validation_msg = f"""
✅ **Arquivo validado com sucesso!**

📄 **Arquivo:** `{result['filename']}`
📝 **Título:** {metadata.get('title', 'N/A')}
📊 **Palavras:** {metadata.get('word_count', 0)}
📏 **Caracteres:** {metadata.get('char_count', 0)}

"""

        if time_check["warnings"]:
            validation_msg += f"⚠️ {time_check['warnings'][0]}\n"
        if time_check["recommendations"]:
            validation_msg += f"💡 {time_check['recommendations'][0]}\n"

        validation_msg += "\n🤖 Processando com GPT-4o-mini..."

        await processing_msg.edit_text(validation_msg, parse_mode="Markdown")

        # 3. Executar pipeline
        pipeline_result = await pipeline.process_pipeline(
            result["file_path"], user_id, metadata
        )

        if pipeline_result["status"] == "success":
            success_msg = f"""
✅ **Pipeline concluído com sucesso!**

🆔 **ID:** `{pipeline_result["execution_id"]}`
📝 **Título:** {pipeline_result.get("title", "N/A")}
⏱️ **Tempo:** {pipeline_result["duration_ms"]}ms
📊 **Palavras originais:** {pipeline_result.get("word_count", 0)}
📏 **Conteúdo final:** {len(pipeline_result["processed_content"])} chars

📋 **Arquivos salvos:**
• `{result['filename']}`
• `{result['filename'].replace('.html', '.metadata.json')}`

🔗 **Post publicado no LinkedIn!**
"""
            await processing_msg.edit_text(success_msg, parse_mode="Markdown")

        else:
            error_msg = f"""
❌ **Erro no pipeline**

🆔 **ID:** `{pipeline_result["execution_id"]}`
⏱️ **Tempo:** {pipeline_result["duration_ms"]}ms
🚨 **Erro:** {pipeline_result["error"]}

📋 **Metadata salvo** com detalhes do erro.
Verifique os logs para mais informações.
"""
            await processing_msg.edit_text(error_msg, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"❌ Erro no handler de documento: {e}")
        await processing_msg.edit_text(f"❌ Erro inesperado: {e}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processar mensagem de texto"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        return

    await update.message.reply_text(
        "📄 Por favor, envie um arquivo HTML para processar.\n"
        "Use /start para ver instruções completas."
    )


def main():
    """Função principal do bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN não configurado")
        return

    logger.info("🚀 Iniciando Telegram Bot v2.5.1...")

    # Criar aplicação
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrar handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    # Log início
    observability.log_csv_event(
        "telegram_bot", "bot_start", True, "", "", "", "", "", 0
    )

    logger.info("✅ Telegram Bot v2.5.1 iniciado com sucesso")
    logger.info(f"📁 Diretório de posts: {os.path.abspath(POSTS_DIR)}")
    logger.info("📋 Sistema de metadata.json ativo")
    logger.info("⏰ Validação de horário ativa")

    # Executar bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

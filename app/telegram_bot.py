#!/usr/bin/env python3
"""
Telegram Bot para receber arquivos HTML e iniciar pipeline de processamento
Integrado com sistema de observabilidade completo
"""
import os
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

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
    """Gerenciador do pipeline Telegram → GPT → LinkedIn"""

    def __init__(self):
        self.processor = PostProcessor()
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

    async def download_file(
        self, document: Document, context: ContextTypes.DEFAULT_TYPE
    ) -> Optional[str]:
        """Baixar arquivo do Telegram"""
        try:
            # Gerar nome único para o arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name = document.file_name or "arquivo.html"
            file_name = f"{timestamp}_{original_name}"
            file_path = os.path.join(POSTS_DIR, file_name)

            # Baixar arquivo
            file = await document.get_file()
            await file.download_to_drive(file_path)

            logger.info(f"📥 Arquivo baixado: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"❌ Erro ao baixar arquivo: {e}")
            return None

    async def process_pipeline(self, file_path: str, user_id: int) -> dict:
        """Executar pipeline completo"""
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

            # 1. Processar com GPT
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

            # 2. Publicar no LinkedIn
            logger.info("🔗 Publicando no LinkedIn...")
            from .linkedin_poster import get_driver, login, publish_post

            driver = None
            try:
                driver = get_driver()
                login(driver, execution_id)
                publish_post(driver, processed_content, execution_id)

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

    message = """
🚀 **LinkedIn Content Pipeline Bot**

Envie um arquivo HTML e eu vou:
1. 📥 Baixar o arquivo
2. 🤖 Processar com GPT-4o-mini
3. 🔗 Publicar no LinkedIn
4. 📊 Registrar na auditoria

**Comandos:**
/start - Mostrar esta mensagem
/status - Ver status do sistema
/stats - Estatísticas de uso
"""

    await update.message.reply_text(message, parse_mode="Markdown")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /status"""
    user_id = update.effective_user.id

    if not pipeline.is_authorized(user_id):
        await update.message.reply_text("❌ Usuário não autorizado")
        return

    # Verificar status dos componentes
    status_msg = "📊 **Status do Sistema:**\n\n"

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
    posts_count = len([f for f in os.listdir(POSTS_DIR) if f.endswith(".html")])
    status_msg += f"📁 Arquivos em posts/: {posts_count}\n"

    await update.message.reply_text(status_msg, parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /stats - Estatísticas do CSV"""
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

        # Contar registros
        with open(csv_file, "r") as f:
            lines = f.readlines()

        total_records = len(lines) - 1  # -1 para header

        if total_records == 0:
            await update.message.reply_text("📊 Nenhuma execução registrada ainda")
            return

        # Análise básica
        telegram_pipelines = len([l for l in lines if "telegram_start" in l])
        successes = len([l for l in lines if ",True," in l])
        failures = len([l for l in lines if ",False," in l])

        success_rate = (successes * 100) // total_records if total_records > 0 else 0

        stats_msg = f"""
📊 **Estatísticas do Pipeline:**

📈 Total de registros: {total_records}
🚀 Pipelines Telegram: {telegram_pipelines}
✅ Sucessos: {successes}
❌ Falhas: {failures}
📊 Taxa de sucesso: {success_rate}%

Para mais detalhes, use o monitor:
`./monitor_logs.sh`
"""

        await update.message.reply_text(stats_msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao obter estatísticas: {e}")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processar arquivo recebido"""
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
        f"📥 Recebido: `{document.file_name}`\n🔄 Iniciando pipeline..."
    )

    try:
        # Baixar arquivo
        file_path = await pipeline.download_file(document, context)
        if not file_path:
            await processing_msg.edit_text("❌ Erro ao baixar arquivo")
            return

        await processing_msg.edit_text(
            f"📥 Arquivo baixado\n🤖 Processando com GPT-4o-mini..."
        )

        # Executar pipeline
        result = await pipeline.process_pipeline(file_path, user_id)

        if result["status"] == "success":
            success_msg = f"""
✅ **Pipeline concluído com sucesso!**

🆔 ID: `{result["execution_id"]}`
⏱️ Tempo: {result["duration_ms"]}ms
📝 Conteúdo: {result["processed_content"][:100]}...

🔗 Post publicado no LinkedIn!
"""
            await processing_msg.edit_text(success_msg, parse_mode="Markdown")

        else:
            error_msg = f"""
❌ **Erro no pipeline**

🆔 ID: `{result["execution_id"]}`
⏱️ Tempo: {result["duration_ms"]}ms
🚨 Erro: {result["error"]}

Verifique os logs para mais detalhes.
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

    logger.info("🚀 Iniciando Telegram Bot...")

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

    logger.info("✅ Telegram Bot iniciado com sucesso")
    logger.info(f"📁 Diretório de posts: {os.path.abspath(POSTS_DIR)}")

    # Executar bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

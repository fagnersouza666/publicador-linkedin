#!/bin/bash
# Script para iniciar o Telegram Bot do LinkedIn Pipeline

set -e

SCRIPT_NAME="LinkedIn Telegram Bot"
BOT_FILE="app/telegram_bot.py"

echo "🤖 $SCRIPT_NAME - Iniciando..."

# Verificar se arquivo existe
if [ ! -f "$BOT_FILE" ]; then
    echo "❌ Arquivo não encontrado: $BOT_FILE"
    exit 1
fi

# Verificar .env
if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado"
    echo "💡 Copie .env.example para .env e configure:"
    echo "   cp .env.example .env"
    echo "   # Edite com suas credenciais"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado"
    exit 1
fi

# Verificar/criar ambiente virtual
if [ ! -d ".venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv .venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source .venv/bin/activate

# Instalar/atualizar dependências
echo "📚 Instalando dependências..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Verificar configurações essenciais
echo "🔍 Verificando configurações..."

if ! grep -q "TELEGRAM_BOT_TOKEN=.*[A-Za-z0-9]" .env; then
    echo "❌ TELEGRAM_BOT_TOKEN não configurado no .env"
    echo "💡 Configure seu bot do Telegram:"
    echo "   1. Fale com @BotFather no Telegram"
    echo "   2. Crie um novo bot com /newbot"
    echo "   3. Copie o token para TELEGRAM_BOT_TOKEN no .env"
    exit 1
fi

if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "❌ OPENAI_API_KEY não configurado no .env"
    echo "💡 Configure sua API key da OpenAI:"
    echo "   1. Acesse https://platform.openai.com/api-keys"
    echo "   2. Crie uma nova API key"
    echo "   3. Copie para OPENAI_API_KEY no .env"
    exit 1
fi

# Criar diretório posts se não existir
echo "📁 Preparando diretório de posts..."
mkdir -p posts

# Verificar permissões
if [ ! -w "posts" ]; then
    echo "❌ Sem permissão de escrita no diretório posts/"
    exit 1
fi

# Verificar logs
if [ -d "/logs" ]; then
    LOG_DIR="/logs"
    echo "🐳 Usando logs Docker: $LOG_DIR"
else
    LOG_DIR="logs"
    echo "💻 Usando logs locais: $LOG_DIR"
    mkdir -p "$LOG_DIR"
fi

echo ""
echo "✅ Todas as verificações passaram!"
echo ""
echo "🚀 Iniciando Telegram Bot..."
echo "   📁 Diretório posts: $(pwd)/posts"
echo "   📊 Diretório logs: $LOG_DIR"
echo ""
echo "💡 Para parar o bot, pressione Ctrl+C"
echo "📱 Teste enviando /start para seu bot no Telegram"
echo ""

# Executar bot
python3 -m app.telegram_bot

echo ""
echo "🏁 Bot finalizado" 
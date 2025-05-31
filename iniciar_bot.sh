#!/bin/bash
# 🚀 Publicador LinkedIn - Inicializador Bot Telegram
# Sistema simplificado para publicação no LinkedIn via Telegram

set -e  # Sair em caso de erro

echo "🚀 Publicador LinkedIn - Bot Telegram"
echo "=================================================="

# Verificar se está no diretório correto
if [ ! -f "app/telegram_bot.py" ]; then
    echo "❌ Execute a partir do diretório raiz do projeto"
    echo "   Esperado: app/telegram_bot.py"
    exit 1
fi

echo "🔍 Verificando configurações..."

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado"
    echo "💡 Copie .env.example para .env e configure suas credenciais"
    exit 1
fi

# Carregar variáveis do .env
source .env

# Verificar credenciais obrigatórias
missing_vars=0

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN não configurado"
    missing_vars=1
fi

if [ -z "$LINKEDIN_EMAIL" ] || [ -z "$LINKEDIN_PASSWORD" ]; then
    echo "❌ Credenciais LinkedIn não configuradas"
    missing_vars=1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY não configurado"
    missing_vars=1
fi

if [ $missing_vars -eq 1 ]; then
    echo ""
    echo "💡 Configure essas variáveis no arquivo .env"
    exit 1
fi

echo "✅ Configurações verificadas com sucesso"

echo "📁 Configurando diretórios..."

# Criar diretórios necessários
mkdir -p posts
mkdir -p posts/pendentes
mkdir -p posts/enviados
mkdir -p posts/logs

echo "✅ Diretórios configurados"

# Verificar se venv existe
if [ ! -d ".venv" ]; then
    echo "📦 Criando ambiente virtual Python..."
    python3 -m venv .venv
fi

# Ativar venv
echo "🔧 Ativando ambiente virtual..."
source .venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo ""
echo "📱 Bot pronto para uso!"
echo "💡 Comandos disponíveis:"
echo "   /start - Instruções e status"
echo "   /queue - Ver fila de publicações"
echo "   /approve - Aprovar publicação"
echo "   /cancel - Cancelar publicação"

echo ""
echo "🚀 Iniciando bot..."
echo "💡 Pressione Ctrl+C para parar"

# Executar o bot
python -m app.telegram_bot 
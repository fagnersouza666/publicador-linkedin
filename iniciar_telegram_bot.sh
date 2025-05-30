#!/bin/bash
# 🚀 LinkedIn Publicador - Inicializador Telegram Bot v2.6.0
# Sistema de Filas de Produção (pendentes → enviados)

set -e  # Sair em caso de erro

echo "🚀 LinkedIn Publicador - Telegram Bot v2.6.0"
echo "📁 Sistema de Filas: pendentes → enviados"
echo "📝 Logs por Data: YYYY-MM-DD.log"
echo "=" * 50

# === VERIFICAÇÕES BÁSICAS ===
echo "🔍 Verificando configurações básicas..."

# Verificar se está no diretório correto
if [ ! -f "app/telegram_bot.py" ]; then
    echo "❌ Erro: Execute a partir do diretório raiz do projeto"
    echo "   Esperado: app/telegram_bot.py"
    exit 1
fi

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo "❌ Erro: Arquivo .env não encontrado"
    echo "💡 Dica: Copie .env.example para .env e configure suas credenciais"
    echo "   cp .env.example .env"
    exit 1
fi

# Source das variáveis
echo "📋 Carregando variáveis de ambiente..."
source .env

# === VERIFICAÇÕES DE CREDENCIAIS ===
echo ""
echo "🔑 Verificando credenciais obrigatórias..."

missing_vars=0

# Telegram Bot (obrigatório)
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN não configurado"
    echo "   Configure no .env ou obtenha um token em @BotFather"
    missing_vars=1
fi

# LinkedIn (obrigatório)
if [ -z "$LINKEDIN_EMAIL" ] || [ -z "$LINKEDIN_PASSWORD" ]; then
    echo "❌ Credenciais LinkedIn não configuradas"
    echo "   Configure LINKEDIN_EMAIL e LINKEDIN_PASSWORD no .env"
    missing_vars=1
fi

# OpenAI (obrigatório para GPT-4o-mini)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY não configurado"
    echo "   Configure no .env para processamento GPT-4o-mini"
    missing_vars=1
fi

if [ $missing_vars -eq 1 ]; then
    echo ""
    echo "🚨 Configure as credenciais obrigatórias no arquivo .env"
    exit 1
fi

echo "✅ Credenciais obrigatórias configuradas"

# === VERIFICAÇÕES OPCIONAIS ===
echo ""
echo "🔧 Verificando configurações opcionais..."

if [ -z "$TELEGRAM_AUTHORIZED_USERS" ]; then
    echo "⚠️ TELEGRAM_AUTHORIZED_USERS não configurado (permitirá todos os usuários)"
    echo "   Recomendado: Configure IDs dos usuários autorizados"
fi

if [ -z "$TELEGRAM_ALERT_BOT_TOKEN" ]; then
    echo "⚠️ Alertas Telegram não configurados (opcional)"
fi

if [ -z "$DISCORD_WEBHOOK_URL" ]; then
    echo "⚠️ Alertas Discord não configurados (opcional)"
fi

# === CONFIGURAR DIRETÓRIOS DE PRODUÇÃO ===
echo ""
echo "📁 Configurando sistema de filas de produção..."

mkdir -p posts
mkdir -p posts/pendentes
mkdir -p posts/enviados  
mkdir -p posts/logs

echo "✅ Diretórios criados:"
echo "   📂 posts/pendentes - Arquivos aguardando processamento"
echo "   📤 posts/enviados - Arquivos já processados e publicados"
echo "   📝 posts/logs - Logs diários (YYYY-MM-DD.log)"

# === CONFIGURAR AMBIENTE PYTHON ===
echo ""
echo "🐍 Configurando ambiente Python..."

# Verificar se venv existe
if [ ! -d ".venv" ]; then
    echo "📦 Criando ambiente virtual Python..."
    python3 -m venv .venv
fi

# Ativar venv
echo "🔧 Ativando ambiente virtual..."
source .venv/bin/activate

# Atualizar pip
echo "📦 Atualizando pip..."
python -m pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando/atualizando dependências..."
pip install -r requirements.txt

echo "✅ Ambiente Python configurado"

# === VERIFICAR CONECTIVIDADE ===
echo ""
echo "🌐 Verificando conectividade das APIs..."

# Teste rápido OpenAI
echo "🤖 Testando OpenAI API..."
python -c "
import openai
import os
try:
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    models = client.models.list()
    print('✅ OpenAI API conectando com sucesso')
except Exception as e:
    print(f'⚠️ OpenAI API warning: {e}')
" 2>/dev/null || echo "⚠️ Não foi possível testar OpenAI API"

# Teste Telegram Bot
echo "📱 Testando Telegram Bot..."
python -c "
import requests
import os
token = os.getenv('TELEGRAM_BOT_TOKEN')
try:
    r = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=5)
    if r.status_code == 200:
        data = r.json()
        if data['ok']:
            print(f'✅ Bot Telegram conectando: @{data[\"result\"][\"username\"]}')
        else:
            print('❌ Token Telegram inválido')
    else:
        print('❌ Erro na API Telegram')
except Exception as e:
    print(f'⚠️ Telegram API warning: {e}')
" 2>/dev/null || echo "⚠️ Não foi possível testar Telegram API"

# === MOSTRAR STATUS ATUAL ===
echo ""
echo "📊 Status atual do sistema:"

# Contar arquivos nas filas
pendentes_count=$(ls -1 posts/pendentes/*.html 2>/dev/null | wc -l || echo "0")
enviados_count=$(ls -1 posts/enviados/*.html 2>/dev/null | wc -l || echo "0")  
logs_count=$(ls -1 posts/logs/*.log 2>/dev/null | wc -l || echo "0")

echo "   📂 Fila pendentes: $pendentes_count arquivos"
echo "   📤 Fila enviados: $enviados_count arquivos"
echo "   📝 Logs diários: $logs_count arquivos"

# Log do dia atual
today_log="posts/logs/$(date +%Y-%m-%d).log"
echo "   📅 Log de hoje: $today_log"

# === EXECUTAR BOT ===
echo ""
echo "🚀 Iniciando Telegram Bot v2.6.0..."
echo "💡 Pressione Ctrl+C para parar"
echo ""
echo "📱 Comandos disponíveis no bot:"
echo "   /start - Instruções e status"
echo "   /queue - Status da fila de produção" 
echo "   /status - Configurações do sistema"
echo "   /stats - Estatísticas avançadas"
echo ""
echo "📁 Para usar em Docker:"
echo "   docker-compose up -d"
echo "   docker-compose logs -f linkedin-poster"
echo ""
echo "📦 Volume mount sugerido:"
echo "   -v \$(pwd)/posts:/app/posts"
echo ""

# Executar bot
python -m app.telegram_bot 
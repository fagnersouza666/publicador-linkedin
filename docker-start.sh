#!/bin/bash
# 🐳 Publicador LinkedIn - Inicializador Docker
# Executa o bot em container Docker com todas as dependências

set -e

echo "🐳 Publicador LinkedIn - Docker"
echo "================================"

# Verificar se Docker está rodando
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker não está rodando"
    echo "💡 Inicie o Docker e tente novamente"
    exit 1
fi

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado"
    echo "💡 Copie .env.example para .env e configure suas credenciais"
    exit 1
fi

echo "🔍 Verificando credenciais no .env..."

# Verificar se as variáveis principais estão configuradas
source .env

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

echo "✅ Credenciais verificadas"

# Criar diretórios de volumes
echo "📁 Preparando volumes Docker..."
mkdir -p posts/pendentes posts/enviados posts/logs

echo "🔨 Construindo imagem Docker..."
docker-compose build

echo "🚀 Iniciando container..."
docker-compose up -d

echo ""
echo "✅ Bot iniciado com sucesso!"
echo ""
echo "📱 Comandos úteis:"
echo "   docker-compose logs -f       # Ver logs em tempo real"
echo "   docker-compose stop          # Parar o bot"
echo "   docker-compose restart       # Reiniciar o bot"
echo "   docker-compose down          # Parar e remover container"
echo ""
echo "📊 Status:"
docker-compose ps 
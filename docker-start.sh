#!/bin/bash
# 🐳 Publicador LinkedIn - Inicializador Docker
# Executa o bot em container Docker com todas as dependências

set -e

echo "🐳 Publicador LinkedIn - Docker"
echo "================================"

# Verificar se Docker está rodando
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker não está rodando"
    echo "💡 Inicie o Docker e tente novamente: sudo systemctl start docker"
    exit 1
fi

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado"
    echo "💡 Copie .env.example para .env e configure suas credenciais:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

echo "🔍 Verificando credenciais no .env..."

# Verificar se as variáveis principais estão configuradas
source .env

missing_vars=0

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "seu_token_do_bot_telegram" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN não configurado"
    echo "   🔗 Crie um bot no @BotFather do Telegram"
    missing_vars=1
fi

if [ -z "$LINKEDIN_EMAIL" ] || [ "$LINKEDIN_EMAIL" = "seu.email@gmail.com" ]; then
    echo "❌ LINKEDIN_EMAIL não configurado"
    missing_vars=1
fi

if [ -z "$LINKEDIN_PASSWORD" ] || [ "$LINKEDIN_PASSWORD" = "SuaSenhaSegura123" ]; then
    echo "❌ LINKEDIN_PASSWORD não configurado"
    missing_vars=1
fi

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-proj-sua_api_key_openai" ]; then
    echo "❌ OPENAI_API_KEY não configurado"
    echo "   🔗 Obtenha sua chave em: https://platform.openai.com/api-keys"
    missing_vars=1
fi

if [ $missing_vars -eq 1 ]; then
    echo ""
    echo "💡 Configure essas variáveis no arquivo .env:"
    echo "   nano .env"
    exit 1
fi

echo "✅ Credenciais verificadas"

# Criar diretórios necessários
echo "📁 Preparando estrutura de pastas..."
mkdir -p posts/pendentes posts/enviados posts/logs logs

# Nome da imagem
IMAGE_NAME="publicador-linkedin"

echo "🔨 Construindo imagem Docker..."
docker build -t $IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo "❌ Erro ao construir a imagem Docker"
    exit 1
fi

echo "🚀 Iniciando container..."

# Parar container anterior se existir
docker stop $IMAGE_NAME 2>/dev/null || true
docker rm $IMAGE_NAME 2>/dev/null || true

# Executar o container com network=host
docker run -d \
    --name $IMAGE_NAME \
    --network=host \
    --env-file .env \
    --restart unless-stopped \
    -v $(pwd)/posts:/app/posts:rw \
    -v $(pwd)/logs:/app/logs:rw \
    $IMAGE_NAME

    

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Bot iniciado com sucesso!"
    echo ""
    echo "📱 Comandos úteis:"
    echo "   docker logs -f $IMAGE_NAME       # Ver logs em tempo real"
    echo "   docker stop $IMAGE_NAME          # Parar o bot"
    echo "   docker restart $IMAGE_NAME       # Reiniciar o bot"
    echo "   docker rm -f $IMAGE_NAME         # Parar e remover container"
    echo ""
    echo "📊 Status do container:"
    docker ps --filter name=$IMAGE_NAME
    
    echo ""
    echo "📋 Para ver logs: docker logs -f $IMAGE_NAME"
else
    echo "❌ Erro ao iniciar o container"
    exit 1
fi 
#!/bin/bash

# 🤖 Publicador LinkedIn - Execução Nativa
# Alternativa ao Docker quando há problemas de rede

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logs coloridos
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_info "🤖 Publicador LinkedIn - Execução Nativa"
echo "========================================"

# Verificar se estamos no diretório correto
if [[ ! -f "app/linkedin_poster.py" ]]; then
    log_error "Execute este script na raiz do projeto"
    log_info "Estrutura esperada: ./app/linkedin_poster.py"
    exit 1
fi

# Verificar se o ambiente virtual existe
if [[ ! -d ".venv" ]]; then
    log_error "Ambiente virtual não encontrado"
    log_info "Execute ./install.sh primeiro para configurar o ambiente"
    exit 1
fi

# Ativar ambiente virtual
log_info "Ativando ambiente virtual..."
source .venv/bin/activate
log_success "Ambiente virtual ativado"

# Verificar se as dependências estão instaladas
log_info "Verificando dependências..."
if ! python3 -c "import selenium" 2>/dev/null; then
    log_error "Selenium não encontrado no ambiente virtual"
    log_info "Execute ./install.sh para instalar dependências"
    exit 1
fi

# Verificar arquivo .env
if [[ ! -f ".env" ]]; then
    log_error "Arquivo .env não encontrado"
    log_info "Copie .env.example para .env e configure suas credenciais"
    exit 1
fi

# Configurar variáveis de ambiente para execução nativa
export DOCKER_MODE=false
export PYTHONPATH="$(pwd)"
export PYTHONUNBUFFERED=1

# Criar diretórios se não existirem
mkdir -p posts/pendentes posts/enviados posts/logs logs

log_success "Ambiente configurado com sucesso"
log_info "🚀 Iniciando aplicação..."
echo ""

# Executar aplicação principal
if [[ $# -gt 0 ]]; then
    # Se argumentos foram passados, usar como texto do post
    export POST_TEXT="$*"
    log_info "Texto do post: $POST_TEXT"
fi

python3 app/linkedin_poster.py "$@"

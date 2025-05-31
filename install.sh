#!/bin/bash

# Script de Instalação Nativa - Publicador LinkedIn
# Alternativa ao Docker para resolver problemas de rede bridge

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

# Verificar se está executando como root
if [[ $EUID -eq 0 ]]; then
   log_error "Este script não deve ser executado como root!"
   log_info "Execute como usuário normal: ./install.sh"
   exit 1
fi

log_info "🚀 Iniciando instalação nativa do Publicador LinkedIn"
echo "======================================================"

# Verificar sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    log_success "Sistema: Linux detectado"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    log_warning "Sistema: macOS detectado (suporte limitado)"
else
    log_error "Sistema operacional não suportado: $OSTYPE"
    exit 1
fi

# Verificar Python 3.8+
log_info "Verificando Python..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version | cut -d " " -f 2)
    python_major=$(echo $python_version | cut -d "." -f 1)
    python_minor=$(echo $python_version | cut -d "." -f 2)
    
    if [[ $python_major -eq 3 && $python_minor -ge 8 ]]; then
        log_success "Python $python_version encontrado"
    else
        log_error "Python 3.8+ requerido. Encontrado: $python_version"
        log_info "Instale Python 3.8+ e execute novamente"
        exit 1
    fi
else
    log_error "Python 3 não encontrado!"
    log_info "No Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

# Verificar/Instalar pip e venv
log_info "Verificando pip e venv..."
if ! python3 -m pip --version &> /dev/null; then
    log_warning "pip não encontrado, instalando..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y python3-pip
    fi
fi

if ! python3 -m venv --help &> /dev/null; then
    log_warning "venv não encontrado, instalando..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y python3-venv
    fi
fi

# Instalar navegadores (Chromium, Firefox ou Google Chrome)
log_info "Verificando navegadores disponíveis..."

# Verificar Chromium primeiro (mais simples)
if command -v chromium &> /dev/null || command -v chromium-browser &> /dev/null; then
    if command -v chromium &> /dev/null; then
        chromium_version=$(chromium --version)
        log_success "Chromium encontrado: $chromium_version"
    else
        chromium_version=$(chromium-browser --version)
        log_success "Chromium encontrado: $chromium_version"
    fi
    PREFERRED_BROWSER="chromium"
elif command -v firefox &> /dev/null; then
    firefox_version=$(firefox --version)
    log_success "Firefox encontrado: $firefox_version"
    PREFERRED_BROWSER="firefox"
elif command -v google-chrome &> /dev/null || command -v google-chrome-stable &> /dev/null; then
    if command -v google-chrome &> /dev/null; then
        chrome_version=$(google-chrome --version)
    else
        chrome_version=$(google-chrome-stable --version)
    fi
    log_success "Google Chrome encontrado: $chrome_version"
    PREFERRED_BROWSER="chrome"
else
    log_warning "Nenhum navegador encontrado, instalando Chromium (recomendado)..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Instalar Chromium no Linux (mais simples que Chrome)
        sudo apt-get update
        sudo apt-get install -y chromium-browser chromium-chromedriver
        log_success "Chromium instalado com sucesso"
        PREFERRED_BROWSER="chromium"
    else
        log_error "Instale um navegador manualmente:"
        log_info "- Chromium: sudo apt-get install chromium-browser"
        log_info "- Firefox: sudo apt-get install firefox"
        log_info "- Chrome: https://www.google.com/chrome/"
        exit 1
    fi
fi

# Configurar driver se necessário
case $PREFERRED_BROWSER in
    "chromium")
        log_info "Verificando ChromeDriver para Chromium..."
        if ! command -v chromedriver &> /dev/null; then
            log_warning "ChromeDriver não encontrado, instalando..."
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                sudo apt-get install -y chromium-chromedriver
                log_success "ChromeDriver instalado"
            fi
        else
            chromedriver_version=$(chromedriver --version)
            log_success "ChromeDriver encontrado: $chromedriver_version"
        fi
        ;;
    "firefox")
        log_info "Verificando GeckoDriver para Firefox..."
        if ! command -v geckodriver &> /dev/null; then
            log_warning "GeckoDriver não encontrado, instalando..."
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                # Baixar GeckoDriver mais recente
                GECKO_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
                wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/${GECKO_VERSION}/geckodriver-${GECKO_VERSION}-linux64.tar.gz"
                sudo tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/
                sudo chmod +x /usr/local/bin/geckodriver
                rm /tmp/geckodriver.tar.gz
                log_success "GeckoDriver instalado"
            fi
        else
            geckodriver_version=$(geckodriver --version | head -1)
            log_success "GeckoDriver encontrado: $geckodriver_version"
        fi
        ;;
    "chrome")
        # Código original do Chrome (mantido como fallback)
        log_info "Verificando ChromeDriver para Google Chrome..."
        if ! command -v chromedriver &> /dev/null; then
            log_warning "ChromeDriver não encontrado, instalando..."
            
            # Detectar versão do Chrome
            if command -v google-chrome &> /dev/null; then
                chrome_version=$(google-chrome --version | cut -d " " -f3 | cut -d "." -f1)
            elif command -v google-chrome-stable &> /dev/null; then
                chrome_version=$(google-chrome-stable --version | cut -d " " -f3 | cut -d "." -f1)
            else
                log_error "Chrome não encontrado para detectar versão"
                exit 1
            fi
            
            log_info "Versão do Chrome detectada: $chrome_version"
            
            # Baixar ChromeDriver compatível
            chromedriver_url="https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${chrome_version}"
            chromedriver_version=$(curl -s $chromedriver_url)
            
            if [[ -z "$chromedriver_version" ]]; then
                log_error "Não foi possível detectar versão compatível do ChromeDriver"
                exit 1
            fi
            
            log_info "Baixando ChromeDriver versão $chromedriver_version..."
            
            # Detectar arquitetura
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                chromedriver_zip="chromedriver_linux64.zip"
            elif [[ "$OSTYPE" == "darwin"* ]]; then
                chromedriver_zip="chromedriver_mac64.zip"
            fi
            
            # Baixar e instalar
            wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${chromedriver_version}/${chromedriver_zip}"
            sudo unzip -o /tmp/chromedriver.zip -d /usr/local/bin/
            sudo chmod +x /usr/local/bin/chromedriver
            rm /tmp/chromedriver.zip
            
            log_success "ChromeDriver instalado com sucesso"
        else
            chromedriver_version=$(chromedriver --version)
            log_success "ChromeDriver encontrado: $chromedriver_version"
        fi
        ;;
esac

# Criar/Ativar ambiente virtual
log_info "Configurando ambiente virtual Python..."
if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
    log_success "Ambiente virtual criado"
else
    log_info "Ambiente virtual já existe"
fi

# Ativar ambiente virtual
source .venv/bin/activate
log_success "Ambiente virtual ativado"

# Instalar dependências Python
log_info "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt
log_success "Dependências Python instaladas"

# Criar estrutura de diretórios
log_info "Criando estrutura de diretórios..."
mkdir -p posts/pendentes posts/enviados posts/logs logs
log_success "Estrutura de diretórios criada"

# Verificar arquivo .env
log_info "Verificando configuração..."
if [[ ! -f ".env" ]]; then
    log_warning "Arquivo .env não encontrado"
    log_info "Copiando .env.example para .env..."
    cp .env.example .env
    log_warning "⚠️  IMPORTANTE: Configure suas credenciais no arquivo .env"
    log_info "Edite o arquivo .env com suas credenciais antes de usar"
else
    log_success "Arquivo .env encontrado"
fi

# Configurar navegador preferido no .env
log_info "Configurando navegador preferido no .env..."
if ! grep -q "BROWSER=" .env; then
    echo "BROWSER=${PREFERRED_BROWSER}" >> .env
    log_success "Navegador ${PREFERRED_BROWSER} configurado no .env"
else
    # Atualizar navegador existente
    sed -i "s/^BROWSER=.*/BROWSER=${PREFERRED_BROWSER}/" .env
    log_success "Navegador atualizado para ${PREFERRED_BROWSER} no .env"
fi

# Verificar permissões
log_info "Verificando permissões..."
chmod +x run_native.sh 2>/dev/null || true
chmod +x docker-start.sh 2>/dev/null || true
log_success "Permissões configuradas"

# Teste básico
log_info "Executando teste básico..."
if python3 -c "import selenium; print('Selenium OK')" 2>/dev/null; then
    log_success "Selenium importado com sucesso"
else
    log_error "Erro ao importar Selenium"
    exit 1
fi

# Teste do Chrome
log_info "Testando Chrome + Selenium..."
python3 test_chrome.py
if [[ $? -eq 0 ]]; then
    log_success "Chrome + Selenium funcionando"
else
    log_warning "Chrome + Selenium com problemas (veja output acima)"
fi

# Resumo da instalação
echo ""
log_success "🎉 Instalação nativa concluída com sucesso!"
echo "======================================================"
log_info "📋 Próximos passos:"
echo "1. Configure suas credenciais no arquivo .env"
echo "2. Execute: ./run_native.sh"
echo ""
log_info "📁 Estrutura criada:"
echo "- .venv/          (ambiente virtual Python)"
echo "- posts/pendentes (arquivos para processar)"
echo "- posts/enviados  (arquivos processados)"
echo "- posts/logs      (logs por data)"
echo "- logs/           (logs do sistema)"
echo ""
log_info "🌐 Navegador configurado:"
case $PREFERRED_BROWSER in
    "chromium")
        echo "- Chromium (recomendado para Docker e desenvolvimento)"
        ;;
    "firefox")
        echo "- Firefox (estável e confiável)"
        ;;
    "chrome")
        echo "- Google Chrome (funcionalidade completa)"
        ;;
esac
echo ""
log_warning "⚠️  IMPORTANTE:"
echo "- Configure LINKEDIN_EMAIL e LINKEDIN_PASSWORD no .env"
echo "- Configure TELEGRAM_BOT_TOKEN para o bot Telegram"
echo "- Configure OPENAI_API_KEY para processamento IA"
echo "- Navegador: BROWSER=${PREFERRED_BROWSER} (já configurado)"
echo ""
log_info "🚀 Para executar: ./run_native.sh"
echo "======================================================" 
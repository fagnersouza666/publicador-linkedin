#!/bin/bash
# Script para configurar volume de logs do LinkedIn Bot

set -e

LOG_DIR="/var/log/linkedin"
SCRIPT_NAME="LinkedIn Bot Setup"

echo "🔧 $SCRIPT_NAME - Configurando observabilidade..."

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
    echo "✅ Executando como root"
else
    echo "❌ Este script precisa ser executado como root"
    echo "   sudo $0"
    exit 1
fi

# Criar diretório de logs
echo "📁 Criando diretório de logs: $LOG_DIR"
mkdir -p "$LOG_DIR"

# Configurar permissões
echo "🔐 Configurando permissões..."
chown 1000:1000 "$LOG_DIR"
chmod 755 "$LOG_DIR"

# Verificar espaço em disco
echo "💾 Verificando espaço em disco..."
available_space=$(df -h /var | awk 'NR==2 {print $4}')
echo "   Espaço disponível: $available_space"

# Criar arquivo de exemplo
echo "📄 Criando arquivo de teste..."
echo "$(date): LinkedIn Bot logs directory initialized" > "$LOG_DIR/setup.log"
chown 1000:1000 "$LOG_DIR/setup.log"

# Configurar logrotate (opcional)
LOGROTATE_CONF="/etc/logrotate.d/linkedin-bot"
echo "🔄 Configurando rotação de logs..."
cat > "$LOGROTATE_CONF" << EOF
$LOG_DIR/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 1000 1000
    postrotate
        # Sinal para aplicação recriar logs se necessário
        /bin/true
    endscript
}

$LOG_DIR/*.csv {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    create 644 1000 1000
}
EOF

echo "✅ Setup de observabilidade concluído!"
echo ""
echo "📊 Configuração:"
echo "   📁 Diretório: $LOG_DIR"
echo "   👤 Proprietário: 1000:1000"
echo "   🔄 Logrotate: $LOGROTATE_CONF"
echo ""
echo "🚀 Agora você pode executar:"
echo "   docker-compose up"
echo ""
echo "📈 Para monitorar logs em tempo real:"
echo "   tail -f $LOG_DIR/poster.log"
echo "   tail -f $LOG_DIR/linkedin_audit.csv" 
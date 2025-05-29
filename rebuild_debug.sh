#!/bin/bash

echo "🔨 REBUILD + DEBUG - Publicador LinkedIn"
echo "========================================"

# Remover imagem existente se houver
echo "🗑️ Removendo imagem anterior..."
docker rmi publicador-selenium 2>/dev/null || echo "Nenhuma imagem anterior encontrada"

# Verificar se DISPLAY está configurado
if [ -z "$DISPLAY" ]; then
    echo "⚠️ Variável DISPLAY não encontrada"
    echo "🔧 Configurando DISPLAY padrão..."
    export DISPLAY=:0
fi

echo "📺 DISPLAY: $DISPLAY"

# Permitir conexões X11 (necessário para mostrar navegador)
echo "🔑 Permitindo conexões X11..."
xhost +local:docker > /dev/null 2>&1 || echo "⚠️ xhost não disponível - modo visual pode não funcionar"

# Construir nova imagem forçadamente
echo "🔨 Construindo nova imagem Docker..."
docker build --no-cache --network=host -f Dockerfile.selenium -t publicador-selenium .

# Criar arquivo .env temporário com DEBUG_MODE ativado
echo "🐛 Criando configuração de debug..."
cp .env .env.debug
echo "DEBUG_MODE=true" >> .env.debug

echo "🚀 Iniciando container com NOVA IMAGEM..."
echo "👁️ O navegador será visível se X11 estiver configurado"
echo "📝 Logs detalhados serão exibidos"

# Executar com X11 forwarding
docker run --network=host \
    --env-file .env.debug \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    publicador-selenium

# Limpar arquivo temporário
rm -f .env.debug

echo "👋 Rebuild + Debug finalizado!" 
#!/bin/bash

echo "🐛 PUBLICADOR LINKEDIN - MODO DEBUG DOCKER"
echo "================================================"

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

# Verificar se a imagem já existe
if [[ "$(docker images -q publicador-selenium 2> /dev/null)" == "" ]]; then
    echo "🔨 Construindo imagem Docker (primeira vez)..."
    docker build --network=host -f Dockerfile.selenium -t publicador-selenium .
else
    echo "✅ Imagem já existe, pulando construção..."
fi

# Criar arquivo .env temporário com DEBUG_MODE ativado
echo "🐛 Criando configuração de debug..."
cp .env .env.debug
echo "DEBUG_MODE=true" >> .env.debug

echo "🚀 Iniciando container em modo DEBUG..."
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

echo "�� Debug finalizado!" 
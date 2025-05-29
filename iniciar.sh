#!/bin/bash

# Verificar se a imagem já existe
if [[ "$(docker images -q publicador-selenium 2> /dev/null)" == "" ]]; then
    echo "🔨 Construindo imagem Docker (primeira vez)..."
    docker build --network=host -f Dockerfile.selenium -t publicador-selenium .
else
    echo "✅ Imagem já existe, pulando construção..."
fi

echo "🚀 Iniciando container..."
docker run --network=host --env-file .env publicador-selenium
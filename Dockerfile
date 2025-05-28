# Dockerfile
FROM ubuntu:22.04

# Evitar prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive

# Instalar Python e dependências do sistema
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    firefox \
    chromium-browser \
    chromium-chromedriver \
    wget \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Instalar geckodriver 0.36.0 (compatível com Firefox 139)
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz \
    && tar -xvzf geckodriver-v0.36.0-linux64.tar.gz \
    && chmod +x geckodriver \
    && mv geckodriver /usr/local/bin/ \
    && rm geckodriver-v0.36.0-linux64.tar.gz

# Configurar display virtual
ENV DISPLAY=:99

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos necessários
COPY . /app

# Instalar dependências Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Comando padrão para executar o publicador específico para Docker
CMD ["python3", "docker_run.py"]

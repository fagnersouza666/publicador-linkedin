# Dockerfile com Chromium para maior compatibilidade Docker
FROM python:3.11-slim

# Metadados da imagem
LABEL maintainer="publicador-linkedin"
LABEL description="Bot Telegram para publicação automática no LinkedIn"
LABEL version="2.9.2"

# Evitar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Configurar diretório de trabalho
WORKDIR /app

# Instalar Chromium e Firefox (ambos disponíveis nos repos)
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    firefox-esr \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app/ ./app/
COPY .env.example .

# Configurar ambiente
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
ENV DOCKER_MODE=true
ENV BROWSER=chromium

# Criar diretórios
RUN mkdir -p posts/pendentes posts/enviados posts/logs && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "print('OK')" || exit 1

# Comando padrão
CMD ["python3", "app/linkedin_poster.py"] 
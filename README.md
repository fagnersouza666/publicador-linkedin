# 🚀 Publicador LinkedIn via Telegram

Bot do Telegram simples e direto para publicar no LinkedIn usando IA.

**Versão 2.8.0** - Sistema Dockerizado e Simplificado

## ✨ Como Funciona

1. 📱 Envie um arquivo HTML para o bot no Telegram
2. 🤖 IA processa e melhora o conteúdo automaticamente
3. 📋 Sistema faz revisão e mostra prévia
4. ✅ Você aprova com `/approve`
5. 🔗 Bot publica automaticamente no LinkedIn

## 🏗️ Estrutura Simples

```
posts/
├── pendentes/        # Arquivos aguardando processamento
├── enviados/         # Arquivos já publicados
└── logs/            # Logs por data (YYYY-MM-DD.log)
```

## ⚙️ Instalação

### 🐳 Opção 1: Docker (Recomendado)

```bash
git clone <repository>
cd publicador
cp .env.example .env
# Edite o .env com suas credenciais
./docker-start.sh
```

### 🐍 Opção 2: Local

```bash
git clone <repository>
cd publicador
cp .env.example .env
# Edite o .env com suas credenciais
./iniciar_bot.sh
```

## 🔑 Configurar Credenciais

**Variáveis obrigatórias no .env:**
- `TELEGRAM_BOT_TOKEN` - Token do @BotFather
- `LINKEDIN_EMAIL` - Seu email LinkedIn
- `LINKEDIN_PASSWORD` - Sua senha LinkedIn
- `OPENAI_API_KEY` - Chave da OpenAI para GPT-4o-mini

## 🐳 Comandos Docker

```bash
# Iniciar bot
./docker-start.sh

# Ver logs em tempo real
docker-compose logs -f

# Parar bot
docker-compose stop

# Reiniciar bot
docker-compose restart

# Parar e remover container
docker-compose down

# Reconstruir imagem
docker-compose build --no-cache
```

## 📱 Comandos do Bot

- `/start` - Instruções e status
- `/queue` - Ver fila de publicações
- `/approve` - Aprovar publicação
- `/cancel` - Cancelar publicação

## 🤖 Como Usar

1. **Inicie o bot**: `./docker-start.sh` ou `./iniciar_bot.sh`
2. **No Telegram**: Envie um arquivo `.html` para o bot
3. **Aguarde**: IA processará automaticamente
4. **Revise**: Bot mostrará prévia do conteúdo
5. **Aprove**: Digite `/approve` para publicar

## 📝 Formato do Arquivo HTML

Seu arquivo HTML deve conter o texto que você quer publicar:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Meu Post</title>
</head>
<body>
    <p>Conteúdo do seu post para o LinkedIn...</p>
</body>
</html>
```

## 🔒 Segurança

- ✅ Credenciais em variáveis de ambiente
- ✅ Container isolado com usuário não-root
- ✅ Aprovação manual obrigatória
- ✅ Logs de todas as ações
- ✅ Validação de conteúdo antes da publicação

## 📊 Sistema de Logs

- 📝 Logs organizados por data: `posts/logs/YYYY-MM-DD.log`
- 📂 Arquivos organizados em `pendentes` → `enviados`
- 🔍 Rastreamento completo de todas as operações
- 🐳 Logs Docker: `docker-compose logs -f`

## 🚨 Troubleshooting

**Docker não inicia:**
- Verifique se o Docker está rodando: `docker info`
- Verifique credenciais no `.env`

**Bot não conecta:**
- Verifique logs: `docker-compose logs -f`
- Teste credenciais manualmente

**Erro no LinkedIn:**
- LinkedIn pode ter captcha - teste manualmente
- Verifique se o container tem acesso à internet

**Erro OpenAI:**
- Verifique se a chave API está correta
- Confirme se tem créditos na conta OpenAI

## 📋 Dependências

### Docker (Incluído na Imagem):
- Python 3.11
- Selenium + Chromium
- python-telegram-bot
- OpenAI
- BeautifulSoup4

### Sistema Local:
- Python 3.8+
- Chrome/Chromium instalado

## 📈 Changelog Recente

### v2.8.0 - Sistema Dockerizado
- ✅ Dockerfile otimizado com Python 3.11
- ✅ docker-compose.yml com volumes persistentes
- ✅ Script `docker-start.sh` para facilitar uso
- ✅ Container isolado com usuário não-root
- ✅ Health checks e logs organizados
- ✅ Suporte tanto Docker quanto execução local

### v2.7.0 - Sistema Simplificado
- ✅ Removido Docker e scripts complexos
- ✅ Criado inicializador shell simples (`iniciar_bot.sh`)
- ✅ Mantido apenas fluxo essencial: Telegram → IA → LinkedIn
- ✅ Estrutura de pastas simplificada
- ✅ README focado e direto

---

**Desenvolvido para automatizar publicações LinkedIn de forma simples e segura** 🚀 
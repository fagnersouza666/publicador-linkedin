# 🚀 Publicador Automático LinkedIn

Automatiza a publicação de posts no LinkedIn usando **pipeline inteligente**: **Telegram → GPT-4o-mini → LinkedIn**.

**Versão 2.5.1** - Arquitetura Modular com Sistema Padronizado

## ✨ Características

- 🤖 **Pipeline Inteligente**: Telegram Bot → GPT-4o-mini → LinkedIn
- 📱 **Bot Telegram**: Recebe arquivos HTML via chat com validações
- 🧠 **Processamento GPT**: Melhora e corrige textos automaticamente
- 🎯 **Publicação Automática**: Posts otimizados direto no LinkedIn
- 📊 **Observabilidade CSV**: Auditoria completa em formato estruturado
- 🚨 **Alertas Inteligentes**: Telegram/Discord em caso de falhas
- 🐳 **Docker Pronto**: Execução isolada com volume persistente
- 🔒 **Seguro**: Configuração com variáveis de ambiente
- 📸 **Screenshots on Error**: Debug automático com capturas de tela

## 🏗️ Arquitetura Modular

### 📁 Estrutura de Módulos

```
app/
├── html_parser.py        # Parser HTML puro (extração e validação)
├── post_processor.py     # Processamento GPT-4o-mini
├── telegram_bot.py       # Bot Telegram com validações
└── linkedin_poster.py    # Automação LinkedIn + observabilidade
```

### 🔄 Pipeline Workflow

```
1. 📥 Telegram → Receber arquivo HTML
2. ✅ Validar conteúdo e horário
3. 📄 Extrair texto + metadados
4. 🤖 Processar com GPT-4o-mini
5. 🔗 Publicar no LinkedIn
6. 💾 Salvar metadata.json
7. 📊 Registrar CSV audit
```

## 📋 Sistema de Arquivos Padronizado

### 📁 Formato de Arquivos

```
posts/
├── 20241220_143025_inteligencia-artificial-educacao.html
├── 20241220_143025_inteligencia-artificial-educacao.metadata.json
├── 20241220_151530_futuro-trabalho-remoto.html
└── 20241220_151530_futuro-trabalho-remoto.metadata.json
```

### 📊 Estrutura metadata.json

```json
{
  "file_path": "posts/20241220_143025_ia-educacao.html",
  "title": "Inteligência Artificial na Educação",
  "word_count": 156,
  "char_count": 987,
  "telegram": {
    "user_id": 123456789,
    "file_name": "artigo-ia.html",
    "received_at": "2024-12-20T14:30:25"
  },
  "processing": {
    "status": "published",
    "pipeline_id": "tg_20241220_143025_123456789",
    "final_content": "🚀 A revolução da IA na educação...",
    "published_at": "2024-12-20T14:31:45"
  },
  "validation": {
    "html_valid": true,
    "time_check": {
      "warnings": [],
      "recommendations": ["✅ Bom horário para posting (14:30)"]
    }
  }
}
```

## ⚙️ Instalação

### 1. 📦 Configurar Ambiente

```bash
git clone <repository>
cd publicador
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 🔧 Configurar Variáveis

```bash
cp .env.example .env
# Editar .env com suas credenciais
```

### 3. 🔑 Configurações Obrigatórias

```env
# LinkedIn
LINKEDIN_EMAIL=seu.email@gmail.com
LINKEDIN_PASSWORD=SuaSenhaSegura123

# OpenAI (GPT-4o-mini)
OPENAI_API_KEY=sk-proj-sua_api_key_openai

# Telegram Bot
TELEGRAM_BOT_TOKEN=seu_token_do_bot_telegram
TELEGRAM_AUTHORIZED_USERS=123456789,987654321
```

### 4. 🤖 Criar Bot Telegram

1. Conversar com [@BotFather](https://t.me/BotFather)
2. Executar `/newbot`
3. Escolher nome e username
4. Copiar token para `.env`
5. Obter seu ID: `/start` em [@userinfobot](https://t.me/userinfobot)

## 🚀 Uso

### 📱 Bot Telegram

```bash
# Iniciar bot
./iniciar_telegram_bot.sh

# Ou Python direto
python -m app.telegram_bot
```

### 💬 Comandos do Bot

- `/start` - Instruções e status de horário
- `/status` - Verificar configurações do sistema
- `/stats` - Estatísticas avançadas com metadata

### 📤 Envio de Arquivos

1. 📄 Envie arquivo HTML para o bot
2. ✅ Receba validação automática
3. ⏰ Veja recomendações de horário
4. 🤖 Aguarde processamento GPT
5. 🔗 Receba confirmação de publicação

### ⏰ Validações de Horário

**Horários Ideais (LinkedIn):**
- 📅 **Dias úteis**: Segunda a sexta
- 🕐 **Horários**: 8h-18h (melhor: 8h-10h, 17h-19h)
- ⚠️ **Evitar**: Fins de semana e horários noturnos

## 🐳 Docker

### 🔧 Configuração

```yaml
# docker-compose.yml
volumes:
  - /var/log/linkedin:/logs:rw
  - linkedin-cache:/app/.cache
```

### 🚀 Execução

```bash
# Configurar logs
sudo ./setup_logs.sh

# Subir containers
docker-compose up -d
```

## 📊 Monitoramento

### 📈 Logs em Tempo Real

```bash
# Monitor interativo
./monitor_logs.sh

# Opções disponíveis:
1) Logs em tempo real
2) Análise CSV completa  
3) Filtrar erros
4) Screenshots de erro
5) Estatísticas do sistema
6) Buscar termo
7) Atividade recente
8) Status dos componentes
```

### 📋 Auditoria CSV

```csv
timestamp,execution_id,action,success,post_text,current_url,error_type,error_msg,screenshot_path,duration_ms
2024-12-20 14:30:25,tg_20241220_143025_123,telegram_start,True,"","file://posts/ia.html","","","",0
2024-12-20 14:30:45,tg_20241220_143025_123,gpt_processing,True,"🚀 A revolução da IA...","file://posts/ia.html","","","",1250
2024-12-20 14:31:20,tg_20241220_143025_123,pipeline_complete,True,"🚀 A revolução da IA...","https://linkedin.com/feed/","","","",2840
```

## 🔧 Testes

### 🧪 Testes Individuais

```bash
# Testar parser HTML
python app/html_parser.py arquivo.html

# Testar processamento GPT
python app/post_processor.py arquivo.html

# Testar pipeline completo
python test_pipeline.py
```

### 📊 Exemplo de Validação

```bash
✅ Arquivo válido!
📊 Estatísticas: {
  'char_count': 1250,
  'word_count': 205,
  'title': 'IA na Educação',
  'has_title': True
}
📄 Texto extraído: 1250 caracteres
📝 Título: IA na Educação
🔗 Slug: ia-na-educacao
```

## 🚨 Alertas

### 📢 Telegram Alerts

```markdown
🚨 **Erro no Pipeline Telegram**

**Erro:** TimeoutException: Element not found
**URL:** https://linkedin.com/feed/
**Arquivo:** posts/20241220_143025_artigo.html
**Tempo:** 2024-12-20 14:30:25

**Screenshot:** /logs/error_20241220_143025.png
```

### 🎯 Discord Webhooks

```json
{
  "content": "🚨 **Falha na Publicação LinkedIn**",
  "embeds": [{
    "title": "Pipeline Error",
    "description": "NoSuchElementException em //*[@data-test='share-box']",
    "color": 15158332,
    "timestamp": "2024-12-20T14:30:25.000Z"
  }]
}
```

## 📈 Analytics

### 🔍 Consultas SQL-like

```python
import pandas as pd

# Carregar dados
df = pd.read_csv('logs/linkedin_audit.csv')

# Taxa de sucesso
success_rate = df['success'].mean() * 100

# Posts por horário
df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
best_hours = df.groupby('hour')['success'].mean()

# Performance por dia da semana
df['weekday'] = pd.to_datetime(df['timestamp']).dt.day_name()
weekday_performance = df.groupby('weekday')['success'].mean()
```

### 📊 Dashboards

- **📈 Grafana**: Conectar ao CSV para dashboards
- **📋 Excel/Sheets**: Importar CSV para análises
- **🔍 Jupyter**: Análises avançadas com pandas

## 🔧 Troubleshooting

### ❌ Problemas Comuns

**Bot não responde:**
```bash
# Verificar token
echo $TELEGRAM_BOT_TOKEN

# Verificar usuários autorizados
echo $TELEGRAM_AUTHORIZED_USERS

# Logs do bot
tail -f logs/app.log | grep telegram
```

**Erro GPT-4o-mini:**
```bash
# Verificar API key
echo $OPENAI_API_KEY

# Teste de conectividade
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

**LinkedIn falha:**
```bash
# Screenshots de debug
ls logs/error_*.png

# Logs específicos
grep "linkedin" logs/linkedin_audit.csv
```

## 📝 Changelog

### v2.5.1 (2024-12-20)

**🏗️ REFATORAÇÃO MODULAR COMPLETA:**

**Separação de Módulos:**
- ✅ `html_parser.py` - Parser HTML puro e independente
- ✅ `post_processor.py` - Processamento GPT focado
- ✅ `telegram_bot.py` - Bot com validações avançadas
- ✅ `linkedin_poster.py` - Automação + observabilidade

**Sistema de Arquivos Padronizado:**
- ✅ Nomenclatura: `YYYYMMDD_HHMMSS_slug-titulo.html`
- ✅ Metadata JSON completo para cada arquivo
- ✅ Tracking de status: received → processing → published/error

**Validações Avançadas:**
- ✅ Conteúdo HTML (tamanho, estrutura, metadados)
- ✅ Horário de posting (dias úteis, horários ideais)
- ✅ Slug automático com remoção de acentos
- ✅ Prevenção de conflitos de nome

**Melhorias de UX:**
- ✅ Mensagens informativas com progresso
- ✅ Estatísticas detalhadas com metadata
- ✅ Recomendações de horário em tempo real
- ✅ Arquivos temporários com limpeza automática

## 📄 Licença

MIT License - Veja LICENSE para detalhes.

---

**Versão Atual**: 2.5.1 | **Última Atualização**: 2024-12-20 | **Módulos**: Separados e Otimizados 
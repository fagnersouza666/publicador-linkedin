# 🚀 Publicador Automático LinkedIn

Automatiza a publicação de posts no LinkedIn usando **pipeline inteligente**: **Telegram → GPT-4o-mini → LinkedIn**.

**Versão 2.5.0** - Pipeline Completo de Automação de Conteúdo

## ✨ Características

- 🤖 **Pipeline Inteligente**: Telegram Bot → GPT-4o-mini → LinkedIn
- 📱 **Bot Telegram**: Recebe arquivos HTML via chat
- 🧠 **Processamento GPT**: Melhora e corrige textos automaticamente
- 🎯 **Publicação Automática**: Posts otimizados direto no LinkedIn
- 📊 **Observabilidade CSV**: Auditoria completa em formato estruturado
- 🚨 **Alertas Inteligentes**: Telegram/Discord em caso de falhas
- 🐳 **Docker Pronto**: Execução isolada com volume persistente
- 🔒 **Seguro**: Configuração com variáveis de ambiente
- 📸 **Screenshots on Error**: Debug automático com capturas de tela

## 🔄 Pipeline Workflow

```
📱 Telegram Bot
    ↓ (recebe arquivo HTML)
📥 Download para /posts
    ↓ 
🤖 GPT-4o-mini
    ↓ (extrai + melhora + corrige)
📝 Conteúdo Otimizado
    ↓
🔗 LinkedIn Poster
    ↓
✅ Post Publicado + 📊 Log CSV
```

## 📋 Estrutura do Projeto

```
publicador/
├── app/
│   ├── linkedin_poster.py      # 🎯 Código principal com observabilidade
│   ├── telegram_bot.py         # 🤖 Bot Telegram para receber arquivos
│   └── post_processor.py       # 🧠 Processador GPT-4o-mini
├── posts/                      # 📁 Arquivos HTML recebidos
├── logs/                       # 📊 Logs rotativos e screenshots
│   ├── poster.log              # 📝 Logs detalhados
│   ├── linkedin_audit.csv      # 📈 Auditoria estruturada
│   └── fail_*.png              # 📸 Screenshots de erro
├── iniciar_telegram_bot.sh     # 🚀 Iniciar bot Telegram
├── test_pipeline.py            # 🧪 Teste completo do pipeline
├── docker-compose.yml          # 🐳 Configuração Docker + volumes
├── requirements.txt            # 📚 Dependências (+ Telegram + OpenAI)
├── .env.example               # 🔐 Modelo completo
└── README.md                  # 📖 Este arquivo
```

## 🚀 Execução Rápida

### 🤖 Pipeline Telegram → GPT → LinkedIn

```bash
# 1. Configurar credenciais
cp .env.example .env
# Editar .env com suas credenciais (Telegram + OpenAI + LinkedIn)

# 2. Iniciar bot Telegram
./iniciar_telegram_bot.sh

# 3. Testar pelo Telegram:
#    - Envie /start para seu bot
#    - Envie um arquivo HTML
#    - Aguarde processamento automático
```

### 🧪 Teste do Pipeline

```bash
# Testar todos os componentes
python test_pipeline.py
```

### 🐳 Docker (tradicional)

```bash
# Setup do volume de logs
sudo ./setup_logs.sh

# Executar
./iniciar.sh

# Monitorar
./monitor_logs.sh
```

## 🔧 Configuração (.env)

```env
# === CREDENCIAIS LINKEDIN ===
LINKEDIN_EMAIL=seu.email@gmail.com
LINKEDIN_PASSWORD=SuaSenhaSegura123

# === PIPELINE TELEGRAM → GPT → LINKEDIN ===
# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:ABC123defHIJKLmnopQRSTuvwXYZ
TELEGRAM_AUTHORIZED_USERS=123456789,987654321

# OpenAI API para processamento
OPENAI_API_KEY=sk-proj-sua_api_key_openai

# === ALERTAS E NOTIFICAÇÕES ===
# Telegram (alertas)
TELEGRAM_CHAT_ID=123456789

# Discord Webhook (opcional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123/ABC123

# === CONFIGURAÇÕES TÉCNICAS ===
BROWSER=chromium
DEBUG_MODE=false
```

## 🤖 Bot Telegram - Comandos

### Comandos Disponíveis
- `/start` - Instruções e boas-vindas
- `/status` - Status do sistema (OpenAI, LinkedIn, etc.)
- `/stats` - Estatísticas do pipeline via CSV

### Workflow do Bot
1. **Envie arquivo HTML** para o bot
2. **Validação automática** (formato, tamanho)
3. **Download** para diretório `/posts`
4. **Processamento GPT-4o-mini**: extração + melhoria + correção
5. **Publicação LinkedIn** automática
6. **Confirmação** com ID de execução e métricas

### Validações de Segurança
- ✅ **Usuários autorizados** (`TELEGRAM_AUTHORIZED_USERS`)
- ✅ **Apenas arquivos HTML** (.html)
- ✅ **Limite de tamanho** (10MB)
- ✅ **Timeout de processamento** (60s)

## 🧠 Processador GPT-4o-mini

### Funcionalidades
- 📄 **Extração inteligente** de texto de HTML
- 🎯 **Otimização para LinkedIn** (1300 chars max)
- ✅ **Correção gramatical** automática
- 📊 **Validação de conteúdo** (hashtags, emojis)
- 🏷️ **Hashtags relevantes** (3-5 automáticas)

### Prompt de Otimização
```
DIRETRIZES:
1. Tom: Profissional mas acessível
2. Tamanho: Máximo 1300 caracteres
3. Estrutura: Gancho + desenvolvimento + call-to-action
4. Hashtags: 3-5 relevantes no final
5. Emojis: Usar com moderação (2-3 máximo)
6. Engajamento: Pergunta ou convite à discussão
```

## 📊 Sistema de Observabilidade Expandido

### 🗂️ Log CSV - Novos Eventos
```csv
timestamp,execution_id,action,success,post_text,current_url,error_type,error_msg,screenshot_path,duration_ms
2024-12-20T16:00:15,tg_20241220_160015_123,telegram_start,True,,file://posts/article.html,,,,0
2024-12-20T16:00:18,tg_20241220_160015_123,gpt_processing,True,"🚀 A IA está...",file://posts/article.html,,,,3000
2024-12-20T16:00:25,tg_20241220_160015_123,login,True,,https://linkedin.com/feed/,,,,2500
2024-12-20T16:00:35,tg_20241220_160015_123,publish_post,True,"🚀 A IA está...",https://linkedin.com/feed/,,,,5000
2024-12-20T16:00:37,tg_20241220_160015_123,pipeline_complete,True,"🚀 A IA está...",https://linkedin.com/feed/,,,,22000
```

### 📈 Novos Tipos de Ação
- `telegram_start` - Início do pipeline via bot
- `gpt_processing` - Processamento com GPT-4o-mini
- `pipeline_complete` - Sucesso completo do pipeline
- `pipeline_error` - Erro em qualquer etapa

## 🔧 Setup Detalhado

### 🤖 Configurar Bot Telegram

1. **Criar bot**: Fale com [@BotFather](https://t.me/botfather)
2. **Comando**: `/newbot`
3. **Nome**: LinkedIn Content Bot (ou escolha sua)
4. **Username**: seu_linkedin_bot
5. **Token**: Copiar para `TELEGRAM_BOT_TOKEN`

### 🔍 Obter seu Chat ID
```bash
# Envie /start para @userinfobot
# Ou use este método:
curl https://api.telegram.org/bot<TOKEN>/getUpdates
```

### 🧠 Configurar OpenAI API

1. **Acesse**: https://platform.openai.com/api-keys
2. **Crie nova chave**: "LinkedIn Pipeline Key"
3. **Copie**: Para `OPENAI_API_KEY`
4. **Modelos suportados**: gpt-4o-mini (recomendado)

### 🔐 Configurar Usuários Autorizados
```env
# IDs separados por vírgula
TELEGRAM_AUTHORIZED_USERS=123456789,987654321

# Para obter seu ID, envie /start para @userinfobot
```

## 🧪 Testes e Validação

### Teste Completo
```bash
python test_pipeline.py
```

**Testa:**
- ✅ Configurações (Telegram, OpenAI, LinkedIn)
- ✅ Diretórios e permissões
- ✅ Extração de texto HTML
- ✅ Processamento GPT-4o-mini
- ✅ Validação de conteúdo
- ✅ Conectividade APIs

### Teste Manual do Processador
```bash
# Criar arquivo HTML de teste
echo '<html><body><h1>Teste IA</h1><p>Inteligência artificial transformando educação...</p></body></html>' > posts/teste.html

# Processar
python -m app.post_processor posts/teste.html
```

## 📱 Exemplo de Uso Telegram

### Conversa de Exemplo
```
Você: /start

Bot: 🚀 LinkedIn Content Pipeline Bot

Envie um arquivo HTML e eu vou:
1. 📥 Baixar o arquivo
2. 🤖 Processar com GPT-4o-mini  
3. 🔗 Publicar no LinkedIn
4. 📊 Registrar na auditoria

Você: [envia arquivo.html]

Bot: 📥 Recebido: artigo.html
🔄 Iniciando pipeline...

Bot: 📥 Arquivo baixado
🤖 Processando com GPT-4o-mini...

Bot: ✅ Pipeline concluído com sucesso!

🆔 ID: tg_20241220_160015_123
⏱️ Tempo: 22000ms
📝 Conteúdo: 🚀 A inteligência artificial está revolucionando a educação...

🔗 Post publicado no LinkedIn!
```

## 🔍 Monitoramento Avançado

### Monitor Interativo Expandido
```bash
./monitor_logs.sh
```

**Novas opções:**
- 📱 **Pipelines Telegram**: Filtrar apenas execuções via bot
- 🤖 **Processamento GPT**: Ver logs de otimização
- 📊 **Métricas de pipeline**: Tempo médio, taxa de sucesso

### Analytics Pipeline
```python
import pandas as pd

# Carregar dados
df = pd.read_csv('logs/linkedin_audit.csv')

# Pipelines Telegram
telegram_pipelines = df[df['execution_id'].str.startswith('tg_')]

# Tempo médio de processamento GPT
gpt_time = df[df['action'] == 'gpt_processing']['duration_ms'].mean()

# Taxa de sucesso por tipo
success_rate = df.groupby('action')['success'].mean() * 100
```

## 🚨 Alertas Expandidos

### Novos Tipos de Alerta
- 🤖 **Erro GPT**: Falha no processamento OpenAI
- 📱 **Bot offline**: Telegram bot fora do ar
- 📁 **Arquivo inválido**: HTML malformado
- ⏱️ **Pipeline timeout**: Processo muito longo

### Exemplo de Alerta
```
🚨 LinkedIn Bot Alert

**Erro**: GPT Processing Failed
**Mensagem**: API rate limit exceeded
**Arquivo**: posts/article_20241220.html
**Execution ID**: tg_20241220_160015_123
**Timestamp**: 2024-12-20 16:00:15
```

## 📊 Performance v2.5.0

- **Pipeline completo**: ~30-60 segundos
- **Processamento GPT**: ~3-10 segundos  
- **Publicação LinkedIn**: ~15-30 segundos
- **Taxa de sucesso**: 95%+ (com retry automático)
- **Arquivos suportados**: até 10MB HTML
- **Conteúdo otimizado**: 1300 chars max (LinkedIn)

## 🆚 Comparação de Versões

| Funcionalidade | v2.4.0 | v2.5.0 |
|----------------|--------|--------|
| **Entrada** | Manual | 🤖 Bot Telegram |
| **Processamento** | Texto direto | 🧠 GPT-4o-mini |
| **Workflow** | 1 etapa | 🔄 Pipeline 3 etapas |
| **Formato** | Texto simples | 📄 HTML → Otimizado |
| **Automação** | Semi-automático | 🚀 Totalmente automático |
| **UX** | Linha de comando | 📱 Chat amigável |

## 🆘 Resolução de Problemas

### ❌ "Bot não responde"
```bash
# Verificar token
./test_pipeline.py

# Verificar logs
./monitor_logs.sh → Opção 1 (Logs principais)

# Reiniciar bot
pkill -f telegram_bot.py
./iniciar_telegram_bot.sh
```

### ❌ "Erro GPT"
```bash
# Verificar API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Ver limite de uso
https://platform.openai.com/usage
```

### ❌ "Arquivo não processado"
```bash
# Verificar formato
file posts/arquivo.html

# Testar extração manual
python -c "
from app.post_processor import extract_text_from_file
print(extract_text_from_file('posts/arquivo.html'))
"
```

## 📝 Exemplo de Pipeline Completo

### Input HTML
```html
<!DOCTYPE html>
<html><body>
<article>
    <h1>O Futuro da Automação</h1>
    <p>A automação está transformando industrias inteiras. 
    Empresas que abraçam essas tecnologias ganham vantagem competitiva 
    significativa, melhorando eficiencia e reduzindo custos operacionais.</p>
</article>
</body></html>
```

### Output LinkedIn Otimizado
```
🚀 A automação está revolucionando indústrias inteiras!

Empresas que abraçam essas tecnologias conquistam vantagem competitiva significativa:

✅ Maior eficiência operacional
✅ Redução de custos
✅ Melhoria na qualidade dos processos

O futuro pertence às organizações que inovam hoje. 

Qual sua experiência com automação na sua área? 👇

#Automacao #Inovacao #Tecnologia #Eficiencia #FuturoDoTrabalho
```

## 🔧 Melhorias v2.5.0 - Pipeline Inteligente

### 🤖 Bot Telegram Completo
- ✅ **3 comandos**: /start, /status, /stats
- ✅ **Validação robusta**: formato, tamanho, usuários
- ✅ **Feedback em tempo real**: progresso step-by-step
- ✅ **Integração observabilidade**: logs + alertas

### 🧠 Processador GPT-4o-mini
- ✅ **Extração inteligente**: BeautifulSoup + priorização de conteúdo
- ✅ **Prompt otimizado**: 7 diretrizes específicas LinkedIn
- ✅ **Validação avançada**: caracteres, hashtags, emojis
- ✅ **Truncamento inteligente**: preserva integridade do texto

### 🔄 Pipeline Orchestration
- ✅ **Workflow assíncrono**: Python asyncio
- ✅ **Error handling**: rollback e cleanup automático
- ✅ **Retry logic**: tentativas automáticas
- ✅ **Timeout management**: limites por etapa

### 📊 Observabilidade Expandida
- ✅ **5 novos eventos**: telegram_start, gpt_processing, etc.
- ✅ **Execution ID único**: formato tg_YYYYMMDD_HHMMSS_user
- ✅ **Métricas detalhadas**: tempo por etapa
- ✅ **Context tracking**: arquivo → GPT → LinkedIn

### 📦 Dependências Adicionadas
- `python-telegram-bot==20.7` - Bot Telegram async
- `openai==1.5.0` - Cliente OpenAI GPT-4o-mini
- `beautifulsoup4==4.12.2` - Parser HTML inteligente

---

**📧 Suporte**: Execute `./test_pipeline.py` para diagnóstico completo  
**🤖 Bot**: Configure TELEGRAM_BOT_TOKEN e inicie com `./iniciar_telegram_bot.sh`  
**🧠 GPT**: Configure OPENAI_API_KEY para processamento inteligente  
**📊 Observabilidade**: CSV em `logs/linkedin_audit.csv` para análise  
**🚨 Alertas**: Configure Telegram/Discord para notificações  
**⭐ Contribuição**: Veja CHANGELOG.md para histórico completo  
**🔄 Versão**: 2.5.0 - Pipeline Inteligente Telegram → GPT → LinkedIn 
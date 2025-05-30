# 🚀 Publicador Automático LinkedIn

Automatiza a publicação de posts no LinkedIn usando **pipeline inteligente**: **Telegram → GPT-4o-mini → Revisão → Aprovação → LinkedIn**.

**Versão 2.6.3** - Sistema de Revisão Pré-Publicação Otimizado e Estrutura Limpa

## ✨ Características Principais

- 🤖 **Pipeline Inteligente**: Telegram Bot → GPT-4o-mini → Revisão IA → LinkedIn
- 📱 **Bot Telegram**: Recebe arquivos HTML via chat com validações completas
- 🧠 **Processamento GPT**: Melhora e corrige textos automaticamente
- 📋 **Revisão IA**: Valida conteúdo **SEM ALTERAR** estilo original
- ⏸️ **Aprovação Manual**: Confirmação obrigatória antes da publicação
- 🎯 **Publicação Segura**: Posts revisados e aprovados direto no LinkedIn
- 📂 **Sistema de Filas**: pendentes → aguardando aprovação → enviados
- 📝 **Logs por Data**: YYYY-MM-DD.log organizados por dia
- 📊 **Observabilidade CSV**: Auditoria completa em formato estruturado
- 🚨 **Alertas Inteligentes**: Telegram/Discord em caso de falhas
- 🐳 **Docker com Volumes**: Execução isolada com persistência
- 🔒 **Seguro**: Configuração com variáveis de ambiente
- 📸 **Screenshots on Error**: Debug automático com capturas de tela

## 🏗️ Sistema de Filas de Produção

### 📁 Estrutura de Arquivos

```
posts/
├── pendentes/                    # Fila de entrada
│   ├── 20241220_143025_ai-educacao.html
│   ├── 20241220_143025_ai-educacao.metadata.json
│   └── 20241220_151530_trabalho-remoto.html
├── enviados/                     # Arquivos processados
│   ├── 20241219_120000_marketing-digital.html
│   ├── 20241219_120000_marketing-digital.metadata.json
│   └── 20241219_140000_inovacao-tech.html
└── logs/                         # Logs diários
    ├── 2024-12-19.log
    ├── 2024-12-20.log
    └── 2024-12-21.log
```

### 🔄 Fluxo de Produção

```
1. 📥 Telegram → Arquivo HTML enviado
2. 📂 Sistema → Adiciona à fila /pendentes
3. ✅ Validação → Conteúdo e horário
4. 🤖 GPT → Processa e otimiza
5. 📋 Revisão IA → Valida sem alterar estilo
6. ⏸️ Aguarda → Aprovação manual obrigatória
7. ✅ Usuário → /approve para confirmar
8. 🔗 LinkedIn → Publica automaticamente
9. 📤 Sistema → Move para /enviados
10. 📝 Log → Registra em YYYY-MM-DD.log
```

### 🏷️ Status de Arquivos

- **pendente**: Aguardando processamento inicial
- **processando**: GPT processando conteúdo
- **aguardando_aprovacao**: Revisão completa, aguardando confirmação
- **publicando**: Aprovado, sendo publicado no LinkedIn
- **publicado**: Sucesso - movido para enviados
- **cancelado**: Cancelado pelo usuário
- **erro**: Falha - mantido em pendentes para retry

## 📋 Sistema de Arquivos Padronizado

### 📊 Estrutura metadata.json

```json
{
  "file_path": "posts/pendentes/20241220_143025_ai-educacao.html",
  "title": "Inteligência Artificial na Educação",
  "word_count": 156,
  "char_count": 987,
  "telegram": {
    "user_id": 123456789,
    "file_name": "artigo-ia.html",
    "received_at": "2024-12-20T14:30:25"
  },
  "processing": {
    "status": "pendente",
    "queue": "pendentes",
    "pipeline_id": "tg_20241220_143025_123456789",
    "moved_to_enviados_at": null
  },
  "production": {
    "daily_log": "2024-12-20.log",
    "queue_position": 3
  }
}
```

## 📋 Sistema de Revisão Pré-Publicação

### 🎯 Sistema de Revisão Inteligente

### 🔍 **OBJETIVO PRINCIPAL**
**Garantir qualidade máxima do conteúdo SEM alterar o estilo original do autor**

O sistema de revisão é o diferencial do projeto - ele **valida e analisa** o conteúdo processado pelo GPT antes da publicação, mas **NUNCA altera o texto** - apenas identifica problemas e sugere melhorias.

### 🧠 **Como Funciona a Revisão**

```
📝 CONTEÚDO ORIGINAL → 🤖 GPT PROCESSA → 📋 IA REVISA → 👤 USUÁRIO APROVA → 🔗 LINKEDIN
```

**Etapas da Revisão:**
1. **Análise Automática**: IA verifica gramática, tom, compliance
2. **Validação Técnica**: Caracteres, hashtags, emojis, políticas
3. **Relatório Estruturado**: JSON com problemas e sugestões
4. **Decisão Humana**: Usuário aprova, cancela ou solicita ajustes

### ✅ **Validações Automáticas Realizadas**

**📊 Análise de Qualidade:**
- ✅ **Gramática e ortografia** - Detecta erros de português
- ✅ **Tamanho adequado** - Verifica limite de 1300 caracteres
- ✅ **Tom profissional** - Avalia adequação para LinkedIn
- ✅ **Hashtags relevantes** - Recomenda 3-5 hashtags
- ✅ **Uso de emojis** - Máximo 5 emojis recomendado
- ✅ **Compliance LinkedIn** - Verifica políticas da plataforma

**🚫 Análise de Conformidade:**
- 🚫 **Conteúdo inadequado** - Detecta linguagem ofensiva
- 🚫 **Spam/clickbait** - Identifica palavras não recomendadas
- 🚫 **Violações de política** - Compliance LinkedIn
- 🚫 **Texto muito longo/curto** - Limites de caracteres

### 📱 **Comandos de Aprovação Disponíveis**

**Fluxo de Aprovação Completo:**
1. 📋 **Sistema faz revisão automática** → Mostra resultado detalhado
2. 👤 **Usuário decide com comandos**:
   - `/approve` - ✅ Aprovar e publicar imediatamente
   - `/cancel` - ❌ Cancelar conteúdo atual
   - `/pending` - 📋 Ver conteúdo aguardando aprovação
   - `/retry` - 🔄 Tentar publicar novamente (se erro)

**Exemplo Real de Revisão no Telegram:**
```
📋 REVISÃO DE CONTEÚDO

✅ Status: APROVADO
🎯 Confiança: 92%

📝 CONTEÚDO FINAL:
🚀 A revolução da IA na educação está transformando como aprendemos e ensinamos. 

Principais benefícios:
• Personalização do aprendizado
• Feedback instantâneo
• Acessibilidade melhorada

#IA #Educacao #Tecnologia #Inovacao

📊 MÉTRICAS:
• Caracteres: 287
• Hashtags: 4
• Emojis: 1

💡 SUGESTÕES:
• Excelente estrutura e tom profissional
• Hashtags bem balanceadas
• Tamanho ideal para engajamento

✅ Aprovar publicação: /approve
❌ Cancelar: /cancel
```

### 🔧 **Configuração Técnica da Revisão**

**Arquivo Principal:** `app/content_reviewer.py`

**Configurações do Prompt de Revisão:**
- 🎯 **Foco**: Validar sem alterar estilo
- 🧠 **Modelo**: GPT-4o-mini (mesmo do processamento)
- 📏 **Limite**: 800 tokens para resposta
- 🌡️ **Temperature**: 0.1 (baixa criatividade)
- 🔒 **Fallback**: Validação local se OpenAI indisponível

**Critérios de Aprovação Automática:**
- ✅ **APPROVE**: Pode publicar diretamente
- ⚠️ **REVIEW_NEEDED**: Requer atenção manual
- ❌ **REJECT**: Não adequado para LinkedIn

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
# Iniciar bot (configura filas automaticamente)
./iniciar_telegram_bot.sh

# Ou Python direto
python -m app.telegram_bot
```

### 💬 Comandos do Bot

- `/start` - Instruções e status da fila atual
- `/queue` - Status detalhado das filas (pendentes/enviados)
- `/status` - Verificar configurações do sistema
- `/stats` - Estatísticas avançadas com metadata

### 📤 Envio de Arquivos

1. 📄 Envie arquivo HTML para o bot
2. 📂 Bot adiciona à fila de **pendentes**
3. ✅ Receba validação e posição na fila
4. ⏰ Veja recomendações de horário
5. 🤖 Aguarde processamento GPT
6. 📤 Arquivo é movido para **enviados**
7. 🔗 Receba confirmação de publicação

### ⏰ Validações de Horário

**Horários Ideais (LinkedIn):**
- 📅 **Dias úteis**: Segunda a sexta
- 🕐 **Horários**: 8h-18h (melhor: 8h-10h, 17h-19h)
- ⚠️ **Evitar**: Fins de semana e horários noturnos

## 🐳 Docker com Volumes

### 🔧 Configuração Atualizada

```yaml
# docker-compose.yml
services:
  linkedin-poster:
    volumes:
      - /var/log/linkedin:/logs:rw
      - ./posts:/app/posts:rw           # 🆕 Volume para filas
      - linkedin-cache:/app/.cache
```

### 🚀 Execução

```bash
# Configurar logs e filas
sudo ./setup_logs.sh

# Subir containers com volumes
docker-compose up -d

# Verificar logs
docker-compose logs -f linkedin-poster
```

### 📦 Comandos Docker

```bash
# Executar com volume mount manual
docker run -d \
  -v $(pwd)/posts:/app/posts:rw \
  -v /var/log/linkedin:/logs:rw \
  --env-file .env \
  linkedin-poster

# Verificar filas
docker exec linkedin-poster ls -la /app/posts/pendentes
docker exec linkedin-poster ls -la /app/posts/enviados

# Acessar logs diários
docker exec linkedin-poster cat /app/posts/logs/$(date +%Y-%m-%d).log
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

### 📝 Logs por Data

```bash
# Log de hoje
tail -f posts/logs/$(date +%Y-%m-%d).log

# Logs específicos
cat posts/logs/2024-12-20.log | grep "ERROR"
cat posts/logs/2024-12-20.log | grep "Pipeline iniciado"

# Últimos logs
ls -la posts/logs/ | tail -5
```

### 📂 Monitoramento de Filas

```bash
# Status das filas
echo "Pendentes: $(ls posts/pendentes/*.html 2>/dev/null | wc -l)"
echo "Enviados: $(ls posts/enviados/*.html 2>/dev/null | wc -l)"

# Próximos na fila
ls -la posts/pendentes/*.html | head -3

# Últimos enviados
ls -la posts/enviados/*.html | tail -3

# Metadata de um arquivo
cat posts/pendentes/20241220_143025_arquivo.metadata.json | jq .
```

### 📋 Auditoria CSV

```csv
timestamp,execution_id,action,success,post_text,current_url,error_type,error_msg,screenshot_path,duration_ms
2024-12-20 14:30:25,tg_20241220_143025_123,telegram_start,True,"","file://posts/pendentes/ai.html","","","",0
2024-12-20 14:30:45,tg_20241220_143025_123,gpt_processing,True,"🚀 A revolução da IA...","file://posts/pendentes/ai.html","","","",1250
2024-12-20 14:31:20,tg_20241220_143025_123,pipeline_complete,True,"🚀 A revolução da IA...","https://linkedin.com/feed/","","","",2840
```

## 🔧 Testes

### 🧪 Testes de Filas

```bash
# Testar sistema de filas
echo "<html><head><title>Teste</title></head><body><h1>Teste IA</h1><p>Conteúdo de teste para o sistema de filas.</p></body></html>" > test.html

# Simular envio via bot (coloque na fila)
cp test.html posts/pendentes/$(date +%Y%m%d_%H%M%S)_teste-sistema.html

# Verificar processamento
python -m app.telegram_bot &
sleep 5
kill %1
```

### 📊 Exemplo de Queue Status

```bash
# Via comando /queue no bot
📊 Status da Fila de Produção:

📂 Pendentes: 3 arquivos
🔄 Próximos na fila:
1. 20241220_143025 - ai na educacao...
2. 20241220_151530 - futuro do trabalho...
3. 20241220_162245 - marketing digital...

📤 Enviados: 15 arquivos
🎉 Últimos enviados:
• 20241220_120000 - inovacao tecnologica...
• 20241219_180000 - sustentabilidade...
• 20241219_140000 - lideranca remota...

📝 Log atual: 2024-12-20.log
```

## 🚨 Alertas

### 📢 Telegram Alerts

```markdown
🚨 **Erro no Pipeline Telegram**

**Erro:** TimeoutException: Element not found
**URL:** https://linkedin.com/feed/
**Arquivo:** posts/pendentes/20241220_143025_artigo.html
**Fila:** pendentes → erro (mantido para retry)
**Log:** 2024-12-20.log
**Tempo:** 2024-12-20 14:30:25

**Screenshot:** /logs/error_20241220_143025.png
```

## 📈 Analytics de Produção

### 🔍 Consultas de Fila

```python
import os
import json
from datetime import datetime

# Analisar filas
def analyze_queues():
    pendentes = len([f for f in os.listdir('posts/pendentes') if f.endswith('.html')])
    enviados = len([f for f in os.listdir('posts/enviados') if f.endswith('.html')])
    
    print(f"📂 Pendentes: {pendentes}")
    print(f"📤 Enviados: {enviados}")
    print(f"📊 Taxa de processamento: {enviados/(pendentes+enviados)*100:.1f}%")

# Analisar logs diários
def analyze_daily_logs():
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = f'posts/logs/{today}.log'
    
    if os.path.exists(log_file):
        with open(log_file) as f:
            lines = f.readlines()
        
        pipelines = len([l for l in lines if "Pipeline iniciado" in l])
        successes = len([l for l in lines if "Pipeline completo" in l])
        errors = len([l for l in lines if "Erro no pipeline" in l])
        
        print(f"📅 Log: {today}")
        print(f"🚀 Pipelines: {pipelines}")
        print(f"✅ Sucessos: {successes}")
        print(f"❌ Erros: {errors}")
```

## 🔧 Troubleshooting

### ❌ Problemas de Fila

**Arquivos presos em pendentes:**
```bash
# Verificar logs do arquivo específico
grep "20241220_143025" posts/logs/2024-12-20.log

# Verificar metadata do arquivo
cat posts/pendentes/20241220_143025_arquivo.metadata.json | jq .processing

# Mover manualmente para enviados (se necessário)
mv posts/pendentes/arquivo.html posts/enviados/
mv posts/pendentes/arquivo.metadata.json posts/enviados/
```

**Logs não sendo criados:**
```bash
# Verificar permissões
ls -la posts/logs/
chmod 755 posts/logs/

# Verificar diretório
mkdir -p posts/logs
```

**Volume Docker não montado:**
```bash
# Verificar mount
docker exec linkedin-poster ls -la /app/posts

# Recriar com volume
docker-compose down
docker-compose up -d
```

## 📝 Changelog

### v2.6.0 (2024-12-20)

**🚀 SISTEMA DE FILAS DE PRODUÇÃO:**

**Separação de Filas:**
- ✅ `/posts/pendentes` - Fila de entrada para novos arquivos
- ✅ `/posts/enviados` - Arquivos processados com sucesso
- ✅ `/posts/logs` - Logs organizados por data (YYYY-MM-DD.log)

**Sistema de Logs por Data:**
- ✅ **Log diário**: Cada dia tem seu próprio arquivo de log
- ✅ **Logger específico**: Pipeline com handler dedicado
- ✅ **Rotação automática**: Logs organizados por data
- ✅ **Metadata tracking**: Status completo por arquivo

**Melhorias de Produção:**
- ✅ **Volume Docker**: `-v $(pwd)/posts:/app/posts:rw`
- ✅ **Comando /queue**: Status detalhado das filas
- ✅ **Retry automático**: Arquivos com erro mantidos em pendentes
- ✅ **Posição na fila**: Tracking de posição e tempo estimado

**Workflow Otimizado:**
- ✅ **Fluxo claro**: pendentes → processando → enviados
- ✅ **Estados consistentes**: Status detalhado por arquivo
- ✅ **Limpeza automática**: Gestão de arquivos temporários
- ✅ **Monitoramento**: Logs diários + CSV audit + metadata JSON

---

## 🎯 **RESUMO EXECUTIVO - Sistema de Revisão Implementado**

### ✅ **O QUE FOI IMPLEMENTADO**

**Sistema de Revisão Pré-Publicação v2.6.2:**
- ✅ **IA revisa o texto antes de publicar SEM mudar o estilo original**
- ✅ **Aprovação manual obrigatória** - Zero publicações automáticas
- ✅ **Comandos de controle**: /approve, /cancel, /pending, /retry
- ✅ **Validação inteligente**: Gramática, compliance, métricas
- ✅ **Fallback local**: Funciona mesmo sem OpenAI API
- ✅ **Sistema de filas**: pendentes → aguardando_aprovacao → enviados

### 🔄 **FLUXO ATUAL DO SISTEMA**

```
1. 📱 Usuário envia HTML via Telegram
2. 🤖 GPT-4o-mini processa e melhora o conteúdo
3. 📋 IA faz revisão SEM alterar estilo
4. 👤 Usuário recebe relatório de revisão
5. ✅ Usuário aprova com /approve
6. 🔗 Sistema publica no LinkedIn
7. 📤 Arquivo movido para /enviados
```

### 🛡️ **SEGURANÇA GARANTIDA**

- **🚫 Zero publicações sem aprovação**: Sistema exige confirmação manual
- **🔍 Revisão inteligente**: IA identifica problemas antes da publicação  
- **📋 Controle total**: Usuário vê exatamente o que será publicado
- **🔄 Retry seguro**: Falhas não publicam conteúdo incorreto
- **📝 Auditoria completa**: Logs detalhados de todas as ações

### 🎨 **PRESERVAÇÃO DO ESTILO**

**O sistema NUNCA altera o estilo original:**
- ✅ **Apenas revisa**: Identifica problemas sem reescrever
- ✅ **Mantém tom**: Preserva a voz do autor
- ✅ **Sugere melhorias**: Dá dicas sem implementar
- ✅ **Decisão humana**: Usuário decide todas as mudanças

### 🚀 **PRONTO PARA PRODUÇÃO**

- ✅ **Testado e validado**: Todos os componentes funcionando
- ✅ **Documentação completa**: README e CHANGELOG atualizados
- ✅ **Docker configurado**: Deploy fácil com volumes persistentes
- ✅ **Monitoramento**: Logs por data e observabilidade CSV
- ✅ **Escalável**: Suporte a múltiplos usuários e filas

---

## 📄 Licença

MIT License - Veja LICENSE para detalhes.

---

**Versão Atual**: 2.6.3 | **Última Atualização**: 2024-12-20 | **Sistema**: Revisão Pré-Publicação com Aprovação Manual 
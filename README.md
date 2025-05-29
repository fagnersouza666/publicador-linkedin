# 🚀 Publicador LinkedIn Automático

**Versão 2.1.4** - Automatizador para publicação de posts no LinkedIn usando Selenium WebDriver.

## 📝 Descrição do Projeto

Este projeto automatiza a publicação de posts no LinkedIn usando Selenium WebDriver. Funciona tanto localmente quanto em containers Docker, com suporte a modo debug visual e múltiplos navegadores.

### ✨ Funcionalidades Principais

- 🔐 **Login automático** no LinkedIn
- 📝 **Publicação automática** de posts
- 🐛 **Modo debug visual** para desenvolvimento
- 🐳 **Suporte completo ao Docker** com resolução de conflitos
- 🌍 **Suporte multi-idioma** (PT, EN, FR, ES)
- 🔄 **Seletores robustos** resistentes a mudanças do LinkedIn
- ⚡ **Otimizado para velocidade** com timeouts inteligentes
- 🛡️ **Proteção contra conflitos** de user-data-dir

## 🛠 Guia de Instalação Passo-a-Passo

### Opção 1: Docker (Recomendado) 🐳

#### Passo 1: Clonar o repositório
```bash
git clone https://github.com/seu-usuario/publicador.git
cd publicador
```

#### Passo 2: Configurar credenciais
```bash
# Copiar template de configuração
cp .env.example .env

# Editar com suas credenciais reais
nano .env  # ou use seu editor favorito
```

#### Passo 3: Configuração do .env (Exemplo Sanitizado)
```env
# === CREDENCIAIS LINKEDIN ===
LINKEDIN_EMAIL=seu.email@gmail.com
LINKEDIN_PASSWORD=SuaSenhaSegura123

# === CONFIGURAÇÕES DO POST ===
POST_TEXT=🚀 Novo post publicado automaticamente com meu bot LinkedIn! #automation #linkedin #python

# === CONFIGURAÇÕES TÉCNICAS ===
BROWSER=chromium
DEBUG_MODE=false
```

#### Passo 4: Executar (Build + Run automático)
```bash
# Execução normal (headless)
./iniciar.sh

# OU execução debug (visual)
./iniciar_debug.sh
```

### Opção 2: Execução Local 💻

#### Passo 1: Preparar ambiente Python
```bash
# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependências com versões pinadas
pip install -r requirements.txt
```

#### Passo 2: Instalar navegador
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install chromium-browser firefox

# macOS
brew install chromium firefox

# Verificar instalação
chromium --version
firefox --version
```

#### Passo 3: Configurar .env (mesmo do Docker)
```bash
cp .env.example .env
# Editar com suas credenciais
```

#### Passo 4: Executar
```bash
# Execução normal
python app/linkedin_poster.py

# Execução debug (modo visual)
python debug_local.py
```

## 📊 Exemplo de Log de Sucesso

### Execução Docker Normal:
```bash
(.venv) user@machine:~/publicador$ ./iniciar.sh
✅ Imagem já existe, pulando construção...
🚀 Iniciando container...
[14:37:36] 🚀 Iniciando Publicador LinkedIn...
[14:37:36] 👻 Modo headless - processo invisível
[14:37:36] 📧 Email: seu.email@gmail.com
[14:37:36] 🌐 Navegador: chromium
[14:37:36] 📝 Texto: 🚀 Novo post publicado automaticamente...
[14:37:36] 🔧 Inicializando navegador...
[14:37:36] 👻 Modo headless ativado (invisível)
[14:37:36] 🌐 Usando Chrome/Chromium...
[14:37:37] 🔐 Iniciando processo de login...
[14:37:37] 📱 Acessando página de login do LinkedIn...
[14:37:38] ✍️ Preenchendo email...
[14:37:39] 🔑 Preenchendo senha...
[14:37:39] 🚀 Clicando no botão de login...
[14:37:46] ⏳ Aguardando resposta do LinkedIn...
[14:37:51] 📍 URL atual: https://www.linkedin.com/feed/
[14:37:51] ✅ Login realizado com sucesso!
[14:37:51] 📝 Iniciando processo de publicação...
[14:37:51] 📰 Navegando para o feed...
[14:38:01] 🎯 Procurando botão 'Começar um post'...
[14:38:01] 🔍 Aguardando elemento com 19 seletores...
[14:40:06] ✅ Elemento encontrado com seletor 16: .share-box-feed-entry__top-bar
[14:40:06] 👆 Clicando no botão para começar post...
[14:40:07] ✅ Clique normal no botão começar post bem-sucedido
[14:40:10] 📝 Procurando área de texto do post...
[14:40:10] 🔍 Aguardando elemento com 14 seletores...
[14:40:10] ✅ Elemento encontrado com seletor 1: .ql-editor[data-placeholder]
[14:40:10] ✍️ Escrevendo o texto do post...
[14:40:11] ✅ Clique normal no área de texto bem-sucedido
[14:40:13] ✅ Texto inserido: 🚀 Novo post publicado automaticamente...
[14:40:13] 🎯 Procurando botão 'Publicar'...
[14:40:13] 🔍 Aguardando elemento com 13 seletores...
[14:40:56] ✅ Elemento encontrado com seletor 9: .share-actions__primary-action
[14:40:56] 🚀 Clicando em 'Publicar'...
[14:40:57] ✅ Clique normal no botão publicar bem-sucedido
[14:41:00] ✅ Comando de publicação enviado!
[14:41:00] ✅ Post publicado com sucesso!
[14:41:00] 🎉 Processo concluído com sucesso!
[14:41:00] 🔚 Fechando navegador...
[14:41:00] 👋 Finalizado!
```

## ⏰ Configuração de Automação (Cron)

### Agendamento com Cron (Linux/Mac)
```bash
# Editar crontab
crontab -e

# Publicar todo dia às 9h da manhã
0 9 * * * cd /caminho/para/publicador && ./iniciar.sh >> /var/log/linkedin-bot.log 2>&1

# Publicar de segunda a sexta às 14h
0 14 * * 1-5 cd /caminho/para/publicador && ./iniciar.sh

# Publicar toda segunda às 8h
0 8 * * 1 cd /caminho/para/publicador && ./iniciar.sh
```

### Script de Agendamento
```bash
#!/bin/bash
# arquivo: agendar_publicacao.sh

cd /caminho/para/publicador

# Atualizar texto do post com data atual
echo "POST_TEXT=📅 Post automático do dia $(date '+%d/%m/%Y')! #automation" > temp.env
cat .env | grep -v POST_TEXT >> temp.env
mv temp.env .env

# Executar publicação
./iniciar.sh

# Log personalizado
echo "$(date): Publicação executada" >> /var/log/linkedin-automation.log
```

## 📦 Dependências Detalhadas

### Python (requirements.txt)
```
selenium==4.21.0      # WebDriver para automação
python-dotenv==1.0.1  # Carregar variáveis .env
```

### Sistema Operacional
- **Docker**: `docker >= 20.0`, `docker-compose >= 1.25`
- **Python**: `>= 3.8`
- **Navegadores locais**: `chromium-browser` ou `firefox`
- **X11** (para modo debug): `xauth`, `xhost`

### Arquivos de Configuração
- **`.env`**: Credenciais e configurações (não committar!)
- **`.env.example`**: Template de configuração
- **`.dockerignore`**: Otimização de build Docker
- **`requirements.txt`**: Dependências Python com versões pinadas

## 🎯 Casos de Uso e Exemplos

### Exemplo 1: Post de Bom Dia Automático
```env
POST_TEXT=🌅 Bom dia, LinkedIn! Começando mais um dia produtivo. Que tal compartilharmos conhecimento hoje? #bomdia #networking #produtividade
```

### Exemplo 2: Post de Conteúdo Técnico
```env
POST_TEXT=🚀 Acabei de automatizar minha presença no LinkedIn com Python e Selenium! 

✅ Login automático
✅ Publicação agendada  
✅ Multi-idioma
✅ Docker ready

Compartilhando no GitHub em breve! #python #automation #selenium #linkedin
```

### Exemplo 3: Post de Reflexão Semanal
```env
POST_TEXT=🔄 Reflexão da semana: A automação não substitui a autenticidade, mas nos libera tempo para focar no que realmente importa - criar conexões genuínas.

O que vocês acham? #automacao #networking #reflexao
```

## 🔧 Versão Atual

**v2.1.4** - Publicador simplificado e otimizado

### Performance v2.1.4:
- **Execução Docker**: ~4 minutos (estável e confiável)
- **Execução Local**: ~1 minuto (otimizada)
- **Taxa de sucesso**: 95%+ (seletores robustos)
- **Compatibilidade**: Multi-idioma global
- **Build Docker**: 30% mais rápido (.dockerignore)
- **Instalação**: 100% confiável (versões pinadas)
- **Estrutura**: Simplificada, apenas arquivos essenciais

## 🐳 Opções Docker

### Execução Padrão (Recomendado)
```bash
# Build e execução simplificados
./iniciar.sh               # Modo normal
./iniciar_debug.sh         # Modo debug

# Ou usando docker-compose
docker-compose up
```

### Docker Compose
```bash
# Execução com configurações otimizadas
docker-compose up

# Em background
docker-compose up -d

# Com rebuild
docker-compose up --build
```

## 🚨 Avisos Importantes

1. **Use com responsabilidade** - Respeite os termos de uso do LinkedIn
2. **Verificação 2FA** - Configure o modo debug para resolver verificações
3. **Rate limiting** - Evite usar excessivamente (máximo 3-5 posts por dia)
4. **Credenciais seguras** - Nunca commite o arquivo .env
5. **Backup de configuração** - Mantenha .env.example atualizado

## 🆘 Troubleshooting

### ❌ Problema: "user data directory already in use"
**✅ RESOLVIDO na v2.1.1** - Agora cada execução usa diretório único

### ❌ Problema: "Botão não encontrado"
**Solução**: Execute em modo debug e verifique se há popups bloqueando
```bash
./iniciar_debug.sh  # Docker
python debug_local.py  # Local
```

### ❌ Problema: "Verificação adicional necessária"
**Solução**: Use modo debug e resolva no celular
1. Execute `./iniciar_debug.sh`
2. Abra app LinkedIn no celular
3. Confirme notificação de login

### ❌ Problema: "ModuleNotFoundError"
**Solução**: Verificar instalação de dependências
```bash
pip install -r requirements.txt
# Ou reinstalar versões específicas
pip install selenium==4.21.0 python-dotenv==1.0.1
```

### ❌ Problema: Docker build muito lento
**Solução**: Usar .dockerignore (já incluído na v2.1.1)
```bash
# Forçar rebuild limpo
docker system prune -f
./iniciar.sh
```

---

**📧 Suporte**: Para problemas, execute com `DEBUG_MODE=true` para logs detalhados.

**⭐ Contribuição**: PRs são bem-vindos! Veja CHANGELOG.md para histórico completo.

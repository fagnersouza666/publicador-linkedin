# 🤖 Publicador Automático LinkedIn

Bot Telegram para publicação automática no LinkedIn com suporte a múltiplos navegadores e observabilidade completa.

## ✨ Funcionalidades

- 🌐 **Múltiplos navegadores**: Chromium, Firefox ou Google Chrome
- 🐳 **Docker & Nativo**: Suporte completo para Docker e instalação nativa
- 📊 **Observabilidade**: Logs CSV, screenshots de erro, alertas Telegram/Discord
- 🤖 **Bot Telegram**: Interface completa para controle remoto
- 🧠 **IA Integrada**: OpenAI para processamento de conteúdo
- 📈 **Auditoria**: Registro completo de todas as ações

## 🚀 Instalação Rápida

### Opção 1: Instalação Nativa (Recomendada) ⭐

```bash
# Clone o repositório
git clone <repository-url>
cd publicador

# Execute a instalação automática
./install.sh

# Configure suas credenciais no .env
nano .env

# Execute o bot
./run_native.sh
```

### Opção 2: Docker (Requer IPv4 forwarding)

```bash
# Clone o repositório
git clone <repository-url>
cd publicador

# Configure suas credenciais
cp .env.example .env
nano .env

# Execute com Docker
./docker-start.sh
```

## 🌐 Navegadores Suportados

| Navegador | Status | Vantagens |
|-----------|--------|-----------|
| **Chromium** | ✅ **Recomendado** | Leve, open source, ideal para Docker |
| **Firefox** | ✅ Funcionando | Estável, suporte completo ao Selenium |
| **Google Chrome** | ⚠️ Configuração complexa | Funcionalidade completa |

O sistema detecta automaticamente o navegador disponível e configura adequadamente.

## 📋 Pré-requisitos

- **Python 3.8+**
- **Um dos navegadores**: Chromium, Firefox ou Chrome
- **Driver correspondente**: ChromeDriver ou GeckoDriver
- **Credenciais LinkedIn**

### Instalação Manual dos Navegadores

```bash
# Ubuntu/Debian - Chromium (Recomendado)
sudo apt-get install chromium-browser chromium-chromedriver

# Ubuntu/Debian - Firefox
sudo apt-get install firefox geckodriver

# Ubuntu/Debian - Google Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update && sudo apt-get install google-chrome-stable
```

## ⚙️ Configuração

### Arquivo .env

```env
# LinkedIn
LINKEDIN_EMAIL=seu_email@exemplo.com
LINKEDIN_PASSWORD=sua_senha

# Telegram Bot
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_AUTHORIZED_USERS=seu_user_id

# OpenAI (Opcional)
OPENAI_API_KEY=sua_chave_openai

# Configurações
BROWSER=chromium
DEBUG_MODE=false
```

### Opções de Navegador

- `BROWSER=chromium` - Chromium (Padrão, recomendado)
- `BROWSER=firefox` - Firefox
- `BROWSER=chrome` - Google Chrome

## 🔧 Uso

### Execução Nativa

```bash
# Execução simples
./run_native.sh

# Com texto específico
./run_native.sh "Meu post no LinkedIn"

# Modo debug (visual)
DEBUG_MODE=true ./run_native.sh
```

### Execução Docker

```bash
# Subir com Docker
./docker-start.sh

# Parar containers
docker-compose down
```

## 📊 Monitoramento

### Logs e Auditoria

- `logs/poster.log` - Log principal da aplicação
- `logs/linkedin_audit.csv` - Auditoria completa em CSV
- `logs/fail_*.png` - Screenshots de erros

### Alertas

O sistema pode enviar alertas via:
- **Telegram** (configure `TELEGRAM_BOT_TOKEN`)
- **Discord** (configure `DISCORD_WEBHOOK_URL`)

## 🔍 Troubleshooting

### Testar Navegadores

```bash
# Testar todos os navegadores disponíveis
python3 test_chrome.py
```

### Problemas Comuns

1. **"Chrome binary not found"**
   - Solução: Use Chromium com `BROWSER=chromium`

2. **"network bridge not found" (Docker)**
   - Solução: Habilite IPv4 forwarding: `sudo sysctl net.ipv4.ip_forward=1`

3. **"Selenium não encontrado"**
   - Solução: Execute `./install.sh` novamente

4. **"Botão não encontrado"**
   - Solução: LinkedIn mudou interface, aguarde atualização

### Logs Detalhados

```bash
# Ativar modo debug
DEBUG_MODE=true ./run_native.sh

# Ver logs em tempo real
tail -f logs/poster.log
```

## 🐳 Docker - Problemas de Rede

Se enfrentar problemas com Docker, execute:

```bash
# Habilitar IPv4 forwarding
sudo sysctl net.ipv4.ip_forward=1

# Tornar permanente
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf

# Reiniciar Docker
sudo systemctl restart docker
```

## 📁 Estrutura do Projeto

```
publicador/
├── app/                    # Código principal
│   └── linkedin_poster.py  # Bot principal
├── posts/                  # Arquivos de posts
│   ├── pendentes/         # Posts para processar
│   ├── enviados/          # Posts processados
│   └── logs/              # Logs por data
├── logs/                   # Logs do sistema
├── .venv/                  # Ambiente virtual Python
├── install.sh              # Instalação nativa
├── run_native.sh           # Execução nativa
├── docker-start.sh         # Execução Docker
├── test_chrome.py          # Teste de navegadores
└── README.md              # Esta documentação
```

## 🔐 Segurança

- Use ambiente virtual Python isolado
- Credenciais em arquivo `.env` (não versionado)
- Container Docker sem privilégios elevados
- Logs com rotação automática

## 📝 Changelog

### v2.9.2 - Suporte Múltiplos Navegadores

- ✅ **Chromium suportado** - Navegador padrão recomendado
- ✅ **Firefox suportado** - Alternativa estável
- ✅ **Detecção automática** - Sistema escolhe melhor navegador
- ✅ **Teste integrado** - `test_chrome.py` para verificar compatibilidade
- ⚠️ **Docker temporariamente limitado** - Problemas de rede em alguns sistemas

### v2.9.1 - Problemas Docker Identificados

- 🐛 **IPv4 forwarding** - Causa raiz dos problemas de rede
- 🔧 **Instalação nativa** - Alternativa robusta implementada
- 📊 **Observabilidade** - Logs CSV e alertas implementados

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

**Status Atual**: ✅ **Funcionando com Chromium/Firefox** | ⚠️ **Docker com limitações de rede** 
# 🚀 Publicador LinkedIn Automático

**Versão 2.1.0** - Automatizador para publicação de posts no LinkedIn usando Selenium WebDriver.

## 📝 Descrição do Projeto

Este projeto automatiza a publicação de posts no LinkedIn usando Selenium WebDriver. Funciona tanto localmente quanto em containers Docker, com suporte a modo debug visual e múltiplos navegadores.

### ✨ Funcionalidades Principais

- 🔐 **Login automático** no LinkedIn
- 📝 **Publicação automática** de posts
- 🐛 **Modo debug visual** para desenvolvimento
- 🐳 **Suporte completo ao Docker**
- 🌍 **Suporte multi-idioma** (PT, EN, FR, ES)
- 🔄 **Seletores robustos** resistentes a mudanças do LinkedIn
- ⚡ **Otimizado para velocidade** com timeouts inteligentes

## 🛠 Instruções de Instalação

### Opção 1: Docker (Recomendado)
```bash
# Clonar o repositório
git clone <url-do-repo>
cd publicador

# Configurar credenciais
cp .env.example .env
# Editar .env com suas credenciais

# Executar
./iniciar.sh               # Modo normal (headless)
./iniciar_debug.sh         # Modo debug (visual)
```

### Opção 2: Local
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar credenciais
cp .env.example .env
# Editar .env com suas credenciais

# Executar
python app/linkedin_poster.py     # Modo normal
python debug_local.py             # Modo debug
```

## 🎯 Exemplos de Uso

### Configuração Básica (.env)
```env
LINKEDIN_EMAIL=seu_email@exemplo.com
LINKEDIN_PASSWORD=sua_senha_segura
POST_TEXT=Seu texto de post aqui!
BROWSER=chromium
DEBUG_MODE=false
```

### Execução Simples
```bash
# Docker - Publicação rápida
./iniciar.sh

# Docker - Modo debug (visualizar processo)
./iniciar_debug.sh

# Local - Direto
python app/linkedin_poster.py
```

### Exemplo de Uso Programático
```python
from app.linkedin_poster import get_driver, login, publish_post

# Configurar
driver = get_driver()
login(driver)
publish_post(driver, "Meu post automático!")
driver.quit()
```

## 📦 Dependências

### Python (requirements.txt)
```
selenium>=4.15.0
python-dotenv>=1.0.0
```

### Sistema
- **Docker**: `docker`, `docker-compose`
- **Local**: `firefox` ou `chromium-browser`
- **X11**: Para modo debug visual

## 📊 Changelog / Atualizações Recentes

### [2.1.0] - 2024-01-15
#### ✨ Adicionado
- **Seletores robustos multi-idioma** (PT, EN, FR, ES)
- **Timeouts otimizados** para execução 3x mais rápida
- **Verificação de sessão** do navegador
- **Tratamento de EOFError** para Docker
- **Screenshots automáticos** para debug

#### 🔧 Melhorado
- **Velocidade de execução** reduzida de ~3min para ~1min
- **Robustez** contra mudanças do LinkedIn
- **Logs mais informativos** com timestamps
- **Tratamento de erros** mais inteligente

#### 🐛 Corrigido
- **Sessões perdidas** do navegador
- **Timeouts excessivos** 
- **Erros de entrada** no Docker
- **Detecção de elementos** mais precisa

### [2.0.0] - 2024-01-14
#### ✨ Adicionado
- **Modo debug visual** completo
- **Suporte Docker** com Selenium Grid
- **Múltiplos navegadores** (Chrome, Firefox, Chromium)
- **Configuração via .env**

## 🔧 Versão Atual

**v2.1.0** - Publicador otimizado com seletores robustos e execução rápida

### Principais Melhorias da v2.1.0:
- ⚡ **Execução 3x mais rápida** (timeouts otimizados)
- 🌍 **Suporte multi-idioma** (funciona em qualquer região)
- 🔄 **19 seletores diferentes** para máxima compatibilidade
- 🛡️ **Resistente a mudanças** do LinkedIn
- 📱 **Verificação automática** de publicação bem-sucedida

---

## 🚨 Avisos Importantes

1. **Use com responsabilidade** - Respeite os termos de uso do LinkedIn
2. **Verificação 2FA** - Configure o modo debug para resolver verificações
3. **Rate limiting** - Evite usar excessivamente para não ser detectado
4. **Credenciais seguras** - Nunca commite o arquivo .env

## 🆘 Troubleshooting

### Problema: "Botão não encontrado"
**Solução**: Execute em modo debug e verifique se há popups bloqueando

### Problema: "Verificação adicional necessária" 
**Solução**: Use `./iniciar_debug.sh` e resolva no celular

### Problema: "Sessão perdida"
**Solução**: LinkedIn pode ter detectado automação - aguarde e tente novamente

---

**📧 Suporte**: Para problemas, execute com `DEBUG_MODE=true` para logs detalhados.

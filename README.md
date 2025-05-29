# Publicador LinkedIn

## Descrição
Automatizador de publicações no LinkedIn usando Python e Selenium.

## ✅ Status: Funcionando Local e Docker!

O projeto está funcionando **perfeitamente tanto na execução local quanto no Docker**.

> **Atenção:** O arquivo `.env` **NUNCA** deve ser enviado para o GitHub. Ele está protegido pelo `.gitignore` e deve conter apenas suas credenciais locais.
> 
> **Dica:** Use o arquivo `.env.example` como modelo seguro. Renomeie para `.env` e preencha com seus dados reais.

### Teste de Diagnóstico Realizado
- ✅ **Local**: Todos os navegadores funcionam, Selenium executa sem problemas
- ✅ **Docker**: Selenium Grid oficial funciona perfeitamente com network host

## 🐛 MODO DEBUG - Visualize o Processo!

Agora você pode **VER O QUE ESTÁ ACONTECENDO** durante a execução:

### Debug Local (Recomendado)
```bash
python debug_local.py
```
- 👁️ **Navegador visível** - veja cada passo da automação
- 📝 **Logs detalhados** - acompanhe todo o processo  
- ⏸️ **Pausa em erros** - inspecione problemas em tempo real
- 🔍 **Feedback completo** - saiba exatamente onde está o problema

### Debug Docker (Avançado)
```bash
./iniciar_debug.sh
```
- Requer X11 configurado no sistema
- Ideal para debug de problemas específicos do container

### Configuração Manual
Adicione no seu `.env`:
```env
DEBUG_MODE=true
```

## 🚀 Execução Recomendada

### Método 1: Local (Mais Rápido)
```bash
python run_local.py
```

### Método 2: Docker (Isolado e Seguro)
```bash
# Script otimizado - só constrói se necessário
./iniciar.sh

# Manualmente
docker run --network=host --env-file .env publicador-selenium

# Ou com docker-compose
docker-compose -f docker-compose.selenium.yml up
```

### Teste de Demonstração
```bash
# Local
python demo.py

# Docker 
./iniciar.sh
```

## Script iniciar.sh ⚡

O script `iniciar.sh` foi otimizado para:
- ✅ **Verificar se a imagem já existe** antes de construir
- ✅ **Pular construção desnecessária** se já tiver a imagem
- ✅ **Executar automaticamente** o container

```bash
./iniciar.sh  # Construção inteligente + execução
```

## 🔧 Scripts Disponíveis

| Script | Descrição | Uso |
|--------|-----------|-----|
| `run_local.py` | Execução local otimizada | `python run_local.py` |
| `debug_local.py` | **Debug visual local** | `python debug_local.py` |
| `demo.py` | Teste sem login real | `python demo.py` |
| `iniciar.sh` | Docker otimizado | `./iniciar.sh` |
| `iniciar_debug.sh` | **Debug visual Docker** | `./iniciar_debug.sh` |

## Instruções de Instalação

### Instalação Local

1. **Crie um ambiente virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou
   .venv\Scripts\activate  # Windows
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o arquivo `.env` com suas credenciais REAIS:**
   - Use o arquivo `.env.example` como base:
     ```bash
     cp .env.example .env
     # Edite o .env com seus dados
     ```
   - Exemplo de conteúdo:
     ```env
     LINKEDIN_EMAIL=seu_email@exemplo.com
     LINKEDIN_PASSWORD=sua_senha_super_secreta
     POST_TEXT=Texto que será publicado automaticamente no LinkedIn.
     BROWSER=firefox  # ou chromium
     DEBUG_MODE=false  # true para ver o processo
     ```

4. **Execute o publicador:**
   ```bash
   # Execução normal
   python run_local.py
   
   # Execução com debug visual
   python debug_local.py
   ```

### Instalação Docker ✅ FUNCIONAL

1. **Script automatizado (recomendado):**
   ```bash
   chmod +x iniciar.sh
   ./iniciar.sh
   ```

2. **Debug Docker (visual):**
   ```bash
   chmod +x iniciar_debug.sh
   ./iniciar_debug.sh
   ```

3. **Construir imagem Selenium manualmente:**
   ```bash
   docker build --network=host -f Dockerfile.selenium -t publicador-selenium .
   ```

4. **Executar:**
   ```bash
   docker run --network=host --env-file .env publicador-selenium
   ```

5. **Usando docker-compose:**
   ```bash
   docker-compose -f docker-compose.selenium.yml up --build
   ```

## Comandos Úteis

### Execução Local
- **Verificar dependências:**
  ```bash
  python run_local.py
  ```

- **Debug visual (ver navegador):**
  ```bash
  python debug_local.py
  ```

- **Teste de demonstração:**
  ```bash
  python demo.py
  ```

### Execução Docker
- **Script otimizado:**
  ```bash
  ./iniciar.sh
  ```

- **Debug visual Docker:**
  ```bash
  ./iniciar_debug.sh
  ```

- **Construir e executar manualmente:**
  ```bash
  docker build --network=host -f Dockerfile.selenium -t publicador-selenium .
  docker run --network=host --env-file .env publicador-selenium
  ```

- **Docker Compose:**
  ```bash
  docker-compose -f docker-compose.selenium.yml up --build
  ```

## Dependências
- Python 3.8+
- **Local**: Firefox ou Chromium/Chrome
- **Docker**: Selenium Grid com Chrome (automático)
- Selenium (com Selenium Manager automático)
- Python-dotenv

## Solução de Problemas

### Problemas de Login
Se suas credenciais estão corretas mas não funciona:

1. **Use o modo debug para visualizar:**
   ```bash
   python debug_local.py
   ```

2. **Verifique os logs detalhados** que mostram:
   - ✅ URL atual após login
   - 🚨 Verificação adicional (se LinkedIn pedir)
   - ❌ Mensagens de erro específicas
   - 📱 Necessidade de verificação por email/SMS

3. **Possíveis causas:**
   - LinkedIn detectou automação e pede verificação
   - Conta com 2FA ativado
   - Localização incomum
   - Muitas tentativas de login

### Execução Local
- **Erro de navegador não encontrado:**
  ```bash
  sudo apt install firefox chromium-browser  # Ubuntu/Debian
  brew install firefox chromium  # macOS
  ```

### Docker 
- **Network bridge not found:**
  ```bash
  docker build --network=host -f Dockerfile.selenium -t publicador-selenium .
  ```

- **Erro de conectividade:**
  ```bash
  docker run --network=host --env-file .env publicador-selenium
  ```

- **Debug visual Docker não funciona:**
  ```bash
  # Verificar X11
  echo $DISPLAY
  xhost +local:docker
  ```

## Versão Atual
2.0.2 - Modo debug visual implementado

## Changelog
### 2024-12-28 v2.0.2
- **🐛 Modo DEBUG visual implementado**
- **Navegador visível** durante execução (local e Docker)
- **Logs detalhados** de cada etapa do processo
- **Pausa em erros** para inspeção em tempo real
- **Scripts debug**: `debug_local.py` e `iniciar_debug.sh`
- **Diagnóstico completo** de problemas de login
- **Múltiplos seletores** para elementos do LinkedIn

### 2024-12-28 v2.0.1
- **⚡ Script `iniciar.sh` otimizado**
- **Verificação inteligente** de imagem existente
- **Construção apenas se necessário** - economiza tempo
- **Execução automática** após verificação

### 2024-12-28 v2.0.0
- **🎉 Docker 100% FUNCIONAL!**
- **Selenium Grid oficial** implementado com sucesso
- **Dockerfile.selenium** com imagem `selenium/standalone-chrome`
- **Network host** resolve conectividade
- **Chrome funciona perfeitamente** no container
- **Script `docker_run_selenium.py`** otimizado

### Versões anteriores
- v1.4.0: Tentativas com Ubuntu básico (limitações identificadas)
- v1.3.0: Foco na execução local como método principal
- v1.2.0: Remoção de dependências manuais de drivers
- v1.1.0: Script de execução local simplificado
- v1.0.0: Implementação inicial com Docker

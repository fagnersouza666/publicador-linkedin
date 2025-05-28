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

## 🚀 Execução Recomendada

### Método 1: Local (Mais Rápido)
```bash
python run_local.py
```

### Método 2: Docker (Isolado e Seguro)
```bash
# Usando Selenium Grid oficial
docker run --network=host --env-file .env publicador-selenium

# Ou com docker-compose
docker-compose -f docker-compose.selenium.yml up
```

### Teste de Demonstração
```bash
# Local
python demo.py

# Docker 
docker run --network=host --env-file .env publicador-selenium
```

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
     ```

4. **Execute o publicador:**
   ```bash
   python run_local.py
   ```

### Instalação Docker ✅ FUNCIONAL

1. **Construir imagem Selenium (recomendado):**
   ```bash
   docker build --network=host -f Dockerfile.selenium -t publicador-selenium .
   ```

2. **Executar:**
   ```bash
   docker run --network=host --env-file .env publicador-selenium
   ```

3. **Usando docker-compose:**
   ```bash
   docker-compose -f docker-compose.selenium.yml up --build
   ```

## Comandos Úteis

### Execução Local
- **Verificar dependências:**
  ```bash
  python run_local.py
  ```

- **Teste de demonstração:**
  ```bash
  python demo.py
  ```

### Execução Docker
- **Construir e executar:**
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

## Versão Atual
2.0.0 - Docker 100% funcional com Selenium Grid

## Changelog
### 2024-03-21 v2.0.0
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

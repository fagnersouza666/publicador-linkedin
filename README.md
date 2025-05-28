# Publicador LinkedIn

## Descrição
Automatizador de publicações no LinkedIn usando Python e Selenium.

## ✅ Status: Funcionando Localmente!

O projeto está funcionando **perfeitamente na execução local**. Para Docker, foram identificadas limitações técnicas fundamentais com navegadores em containers.

### Teste de Diagnóstico Realizado
- ✅ **Local**: Todos os navegadores funcionam, Selenium executa sem problemas
- ❌ **Docker**: Firefox e Chromium falham ao executar, mesmo com drivers corretos

## 🚀 Execução Recomendada (Local)

### Método Simples
```bash
python run_local.py
```
Este script verifica dependências e executa o publicador automaticamente.

### Teste de Demonstração
```bash
python demo.py
```
Testa o navegador sem fazer login real no LinkedIn.

## Instruções de Instalação

### Instalação Local (RECOMENDADO)

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
   ```
   LINKEDIN_EMAIL=seu_email_real@exemplo.com
   LINKEDIN_PASSWORD=sua_senha_real
   POST_TEXT=Texto que será publicado
   BROWSER=firefox  # ou chromium
   ```

4. **Execute o publicador:**
   ```bash
   python run_local.py
   # ou diretamente:
   python app/linkedin_poster.py
   # ou teste:
   python demo.py
   ```

### Docker (Não Funcional - Limitações Técnicas)

⚠️ **Confirmado**: Docker com navegadores gráficos não funciona neste projeto.

**Diagnóstico realizado mostra:**
- Firefox e Chromium falham ao executar no container (código 1)
- Incompatibilidades fundamentais entre navegadores e ambiente container
- Selenium não consegue inicializar drivers corretamente

**Conclusão**: Docker não é viável para este tipo de automação.

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

- **Teste de diagnóstico:**
  ```bash
  python test_docker.py  # Para testar ambiente
  ```

- **Executar diretamente:**
  ```bash
  python app/linkedin_poster.py
  ```

## Dependências
- Python 3.8+
- Firefox ou Chromium/Chrome
- Selenium (com Selenium Manager automático)
- Python-dotenv

## Solução de Problemas

### Execução Local
- **Erro de navegador não encontrado:**
  ```bash
  sudo apt install firefox chromium-browser  # Ubuntu/Debian
  brew install firefox chromium  # macOS
  ```

- **Erro de dependências Python:**
  ```bash
  pip install -r requirements.txt
  ```

- **"Falha no login":**
  - ✅ **Normal se credenciais são de exemplo**
  - Configure credenciais REAIS no arquivo `.env`
  - O LinkedIn pode detectar automação - use com moderação
  - Teste primeiro com `python demo.py`

### Docker 
- **Status**: ❌ Não funcional
- **Motivo**: Limitações técnicas de navegadores em containers
- **Solução**: Use apenas execução local

## 🚀 Enviando para GitHub

### Opção 1: Via Interface Web
1. Crie repositório em [github.com/new](https://github.com/new)
   - Nome: `publicador-linkedin`
   - Público, sem README
2. No terminal deste projeto:
   ```bash
   git remote add origin https://github.com/SEU_USERNAME/publicador-linkedin.git
   git branch -M main
   git push -u origin main
   ```

### Opção 2: Via GitHub CLI
```bash
gh auth login  # autenticar primeiro
gh repo create publicador-linkedin --public --push
```

## Versão Atual
1.4.0 - Confirmação técnica das limitações Docker

## Changelog
### 2024-03-21 v1.4.0
- **Teste diagnóstico conclusivo**: Docker não funciona, local funciona perfeitamente
- **Script de diagnóstico** `test_docker.py` adicionado
- **Documentação final** com evidências técnicas
- **Remoção de esperanças irreais** sobre Docker

### Versões anteriores
- v1.3.0: Foco na execução local como método principal
- v1.2.0: Remoção de dependências manuais de drivers
- v1.1.0: Script de execução local simplificado
- v1.0.0: Implementação inicial com Docker
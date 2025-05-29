# 🚀 Publicador Automático LinkedIn

Automatiza a publicação de posts no LinkedIn usando Python Selenium WebDriver com suporte total ao Docker.

**Versão 2.2.0** - Código unificado e simplificado

## ✨ Características

- 🎯 **Automação Completa**: Faz login e publica posts automaticamente
- 🐳 **Docker Pronto**: Execução isolada com imagem oficial Selenium  
- 🌐 **Navegadores**: Chrome/Chromium e Firefox
- 🎨 **Modo Visual**: Debug com navegador visível
- 🔒 **Seguro**: Configuração com variáveis de ambiente
- 📝 **Logs Detalhados**: Acompanhe cada etapa
- 🌍 **Multi-idioma**: Suporte a PT/EN/FR/ES
- 🔄 **Código Unificado**: Uma única base para Docker e local

## 📋 Estrutura do Projeto

```
publicador/
├── app/
│   └── linkedin_poster.py      # 🎯 Código principal unificado
├── debug_local.py              # 🐛 Debug local visual
├── docker-compose.yml          # 🐳 Configuração Docker
├── Dockerfile.selenium         # 📦 Imagem Docker
├── iniciar.sh                  # ▶️ Script Docker
├── iniciar_debug.sh           # 🔍 Script debug Docker
├── requirements.txt            # 📚 Dependências
├── .env.example               # 🔐 Modelo de configuração
└── README.md                  # 📖 Este arquivo
```

## 🚀 Execução

### 🐳 Docker (Recomendado)

```bash
# 1. Configurar credenciais
cp .env.example .env
# Editar .env com suas credenciais

# 2. Executar
./iniciar.sh

# 3. Debug visual (opcional)
./iniciar_debug.sh
```

### 💻 Local

```bash
# 1. Configurar ambiente
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar credenciais
cp .env.example .env
# Editar .env com suas credenciais

# 4. Executar
python app/linkedin_poster.py

# 5. Debug visual
python debug_local.py
```

## 🔧 Configuração (.env)

```env
# === CREDENCIAIS LINKEDIN ===
LINKEDIN_EMAIL=seu.email@gmail.com
LINKEDIN_PASSWORD=SuaSenhaSegura123

# === CONFIGURAÇÕES DO POST ===
POST_TEXT=🚀 Novo post publicado automaticamente! #automation #linkedin

# === CONFIGURAÇÕES TÉCNICAS ===
BROWSER=chromium        # chromium ou firefox (local)
DEBUG_MODE=false        # true para modo visual
```

## 📦 Dependências

- **Python**: >= 3.8
- **Selenium**: 4.21.0
- **python-dotenv**: 1.0.1
- **Docker**: >= 20.0 (opcional)
- **Navegador**: Chrome/Firefox (execução local)

## 🆘 Resolução de Problemas

### ❌ "Verificação adicional necessária"
```bash
# Use modo debug para resolver no celular
./iniciar_debug.sh  # Docker
python debug_local.py  # Local
```

### ❌ "Botão não encontrado"
```bash
# Execute em modo visual para verificar
DEBUG_MODE=true python app/linkedin_poster.py
```

### ❌ "ModuleNotFoundError"
```bash
# Reinstalar dependências
pip install -r requirements.txt
```

## 📊 Performance v2.2.0

- **Execução Docker**: ~4 minutos (estável)
- **Execução Local**: ~1 minuto (otimizada)
- **Taxa de sucesso**: 95%+ (seletores robustos)
- **Compatibilidade**: Multi-idioma (PT/EN/FR/ES)
- **Manutenção**: Simplificada (código único)

## 📝 Exemplo de Sucesso

```bash
[14:30:15] 🔧 Inicializando navegador...
[14:30:18] 🔑 Fazendo login no LinkedIn...
[14:30:22] ✅ Login realizado com sucesso
[14:30:25] 📝 Iniciando processo de publicação...
[14:30:28] ✅ Post publicado com sucesso!
[14:30:30] 👋 Finalizado!
```

---

**📧 Suporte**: Execute com `DEBUG_MODE=true` para logs detalhados  
**⭐ Contribuição**: Veja CHANGELOG.md para histórico completo  
**🔄 Versão**: 2.2.0 - Código unificado e simplificado
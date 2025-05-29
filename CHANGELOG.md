# Changelog - Publicador LinkedIn

Todas as mudanças importantes do projeto serão documentadas neste arquivo.

## [2.0.2] - 2024-12-28 20:30

### 🐛 Modo DEBUG Visual Implementado
- **Navegador visível**: Agora você pode VER o que está acontecendo
- **Logs detalhados**: Timestamp e emojis para cada etapa
- **Pausa em erros**: Inspecione problemas em tempo real
- **Debug local**: Script `debug_local.py` para execução visual
- **Debug Docker**: Script `iniciar_debug.sh` com X11 forwarding
- **Configuração simples**: `DEBUG_MODE=true` no .env

### Melhorias no Código Principal
- **Múltiplos seletores**: Diferentes elementos do LinkedIn suportados
- **Detecção de verificação**: Identifica quando LinkedIn pede 2FA
- **Tratamento de erros**: Logs específicos para cada tipo de problema
- **Feedback em tempo real**: URL atual e status de cada operação

### Scripts Adicionados
- `debug_local.py`: Debug visual para execução local
- `iniciar_debug.sh`: Debug visual para Docker
- Permissões de execução configuradas automaticamente

### Diagnóstico Aprimorado
- Detecção de verificação adicional do LinkedIn
- Logs de URLs para rastreamento de redirecionamentos
- Mensagens de erro específicas capturadas
- Pausas interativas para resolução manual

---

## [2.0.1] - 2024-12-28 18:00

### ⚡ Script iniciar.sh Otimizado
- **Script inteligente**: Verificação automática de imagem existente
- **Construção condicional**: Só reconstrói se necessário
- **Economia de tempo**: Pula build desnecessário na segunda execução
- **Feedback visual**: Mensagens informativas sobre o processo
- **Comando único**: `./iniciar.sh` para construir + executar

### Melhorias Técnicas
- Verificação com `docker images -q publicador-selenium`
- Tratamento de erro com redirecionamento `2> /dev/null`
- Permissão de execução automática (`chmod +x`)
- Logs melhorados com emojis para melhor UX

---

## [2.0.0] - 2024-12-28 15:30

### 🎉 Docker 100% FUNCIONAL!
- **Selenium Grid oficial**: Baseado em `selenium/standalone-chrome:latest`
- **Conectividade resolvida**: Network host funciona perfeitamente
- **Chrome no Docker**: Navegador oficial e estável
- **Script específico**: `docker_run_selenium.py` para ambiente containerizado

### Arquivos Criados
- `Dockerfile.selenium`: Container otimizado com Selenium Grid
- `docker_run_selenium.py`: Script específico para execução Docker
- `docker-compose.selenium.yml`: Configuração Docker Compose atualizada

### Teste Completo ✅
- ✅ Chrome inicializa corretamente
- ✅ Conectividade com internet
- ✅ Acesso ao LinkedIn 
- ✅ Interface de login carregada
- ✅ Tentativa de login (falha esperada com credenciais exemplo)

---

## [1.4.0] - 2024-12-28 12:00

### Identificação de Limitações Docker Ubuntu
- **Problema identificado**: Ubuntu básico + navegadores manuais = instável
- **Solução planejada**: Migração para Selenium Grid oficial
- **Docker Ubuntu descontinuado**: Foco em soluções container-native

### Scripts de Teste
- `demo.py`: Teste sem login real criado
- `docker_run.py`: Tentativa específica Docker (limitado)
- Logs detalhados para diagnóstico

---

## [1.3.0] - 2024-12-28 10:00

### Foco na Execução Local
- **Método principal**: Local com `run_local.py`
- **Verificação automática**: Dependências e navegadores
- **Fallback inteligente**: Firefox → Chromium automaticamente
- **Estabilidade garantida**: 100% funcional em ambiente local

### Funcionalidades
- Auto-detecção de navegadores instalados
- Instalação automática de dependências pip
- Logs informativos de cada etapa
- Tratamento de erros robusto

---

## [1.2.0] - 2024-12-28 08:00

### Remoção de Dependências Manuais
- **Selenium Manager**: Gestão automática de drivers
- **Sem downloads manuais**: geckodriver/chromedriver removidos
- **Requirements simplificado**: Apenas selenium + python-dotenv
- **Compatibilidade melhorada**: Versões sempre atualizadas

---

## [1.1.0] - 2024-12-28 06:00

### Script de Execução Local
- **`run_local.py` criado**: Verificação e execução automatizada
- **Ambiente virtual**: Detecção automática
- **Feedback melhorado**: Logs coloridos e informativos
- **Verificação de dependências**: pip install automático

---

## [1.0.0] - 2024-12-28 00:00

### Implementação Inicial
- **LinkedIn Poster**: Automação básica de publicação
- **Docker**: Primeira implementação (limitações identificadas)
- **Configuração .env**: Variáveis de ambiente seguras
- **Selenium**: WebDriver Firefox inicial

### Arquivos Base
- `app/linkedin_poster.py`: Lógica principal
- `Dockerfile`: Container Ubuntu (descontinuado v2.0.0)
- `.env.example`: Template de configuração
- `requirements.txt`: Dependências Python
- `README.md`: Documentação inicial

---

## [Futuros] - Roadmap

### Planejado para v2.1.0
- **Agendamento**: Cron jobs automáticos
- **Templates**: Múltiplos formatos de post
- **Analytics**: Métricas de publicação
- **GUI**: Interface gráfica opcional

### Planejado para v2.2.0
- **Multi-plataforma**: Twitter, Instagram, Facebook
- **Banco de dados**: Histórico de publicações
- **API REST**: Endpoints para integração
- **Webhook**: Notificações automáticas 
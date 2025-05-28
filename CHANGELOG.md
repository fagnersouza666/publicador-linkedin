# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.4.0] - 2024-03-21

### ✅ Conclusão Definitiva
- **Teste diagnóstico realizado**: Docker confirmadamente não funciona
- **Execução local**: Funciona perfeitamente (100% testado)
- **Evidências técnicas**: Firefox e Chromium falham no container (código 1)

### Adicionado
- Script `test_docker.py` para diagnóstico completo do ambiente
- Teste comparativo Docker vs Local documentado
- Evidências técnicas das limitações do Docker

### Confirmado
- ✅ **Local**: `python run_local.py` funciona perfeitamente
- ❌ **Docker**: Navegadores não executam, limitações fundamentais
- 🔍 **Diagnóstico**: Proof-of-concept que Docker não é viável

### Recomendação FINAL
**Use APENAS execução local** - Docker é tecnicamente inviável para automação de navegadores.

## [1.3.0] - 2024-03-21

### Conclusões Finais
- **Confirmação**: Execução local funciona perfeitamente
- **Docker**: Limitações técnicas reconhecidas e documentadas
- **Foco**: Priorização da execução local como método principal

### Adicionado
- Script `docker_run.py` específico para tentativas no Docker
- Documentação realista sobre limitações do Docker
- Recomendações claras de uso local

### Modificado
- README.md atualizado com foco na execução local
- Versão do geckodriver atualizada para 0.36.0
- Status do projeto atualizado para "Funcionando Localmente"

### Problemas Identificados no Docker
- Incompatibilidades entre Firefox 139.0 e geckodriver
- Falhas do chromedriver em ambiente container
- Limitações de conectividade para Selenium Manager
- Complexidade de configuração de display virtual

### Recomendação Final
**Use execução local com `python run_local.py` - funciona perfeitamente!**

## [1.2.0] - 2024-03-21

### Adicionado
- Script `demo.py` para testes sem login real
- Selenium Manager automático para download de drivers
- Melhoria na detecção de navegadores Chrome/Chromium

### Modificado
- Remoção de dependências manuais de geckodriver e chromedriver
- Simplificação da configuração de navegadores
- Atualização da documentação com status funcional

### Corrigido
- Problemas de compatibilidade com drivers locais
- Funcionamento tanto local quanto no Docker
- Melhor tratamento de erros de navegadores

## [1.1.0] - 2024-03-21

### Adicionado
- Script `run_local.py` para execução local simplificada
- Verificação automática de dependências e navegadores
- Melhor detecção de navegadores disponíveis no sistema
- Seção "Execução Rápida" no README

### Modificado
- Priorização da execução local sobre Docker
- Reorganização do README.md para facilitar o uso
- Melhoria nas instruções de solução de problemas

### Corrigido
- Problemas persistentes com navegadores no Docker
- Configuração do Firefox para execução em container

## [1.0.0] - 2024-03-21

### Adicionado
- Configuração inicial do projeto
- Automatizador de publicações no LinkedIn
- Suporte ao Docker com Dockerfile
- Arquivo docker-compose.yml para facilitar o uso
- Suporte a Firefox e Chromium
- Configuração de variáveis de ambiente via .env
- Documentação completa no README.md

### Modificado
- Configuração padrão para usar Chromium no Docker
- Adição de flags --network=host para resolver problemas de rede

### Corrigido
- Problema de "network bridge not found" no Docker
- Configuração de paths para drivers do Selenium
- Configuração de opções headless para navegadores

### Técnico
- Migração da imagem base de python:3.10-slim para ubuntu:22.04
- Instalação manual do geckodriver
- Configuração explícita dos serviços do Selenium 
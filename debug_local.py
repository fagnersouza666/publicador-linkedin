#!/usr/bin/env python3
"""
Script de Debug Local para o Publicador LinkedIn
Executa em modo visual para debug
"""
import os

os.environ["DEBUG_MODE"] = "true"
os.environ["DOCKER_MODE"] = "false"

# Importar e executar o publicador
if __name__ == "__main__":
    print("🔍 Iniciando debug local em modo visual...")

    # Importar o módulo principal
    import app.linkedin_poster

    print("✅ Debug concluído!")

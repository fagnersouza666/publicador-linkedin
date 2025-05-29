#!/usr/bin/env python3
"""
Script para debug local do Publicador LinkedIn
- Ativa modo visual (não headless)
- Logs detalhados de cada etapa
- Pausa para inspeção em caso de erro
"""

import os
import sys
import subprocess


def main():
    print("🐛 PUBLICADOR LINKEDIN - MODO DEBUG LOCAL")
    print("=" * 50)

    # Verificar se está em ambiente virtual
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("✅ Ambiente virtual detectado")
    else:
        print("⚠️ Recomendado usar ambiente virtual:")
        print("   python -m venv .venv")
        print("   source .venv/bin/activate")
        print()

    # Verificar dependências
    try:
        import selenium
        from dotenv import load_dotenv

        print("✅ Dependências encontradas")
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("🔧 Instalando automaticamente...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("✅ Dependências instaladas!")

    # Verificar arquivo .env
    if not os.path.exists(".env"):
        print("❌ Arquivo .env não encontrado!")
        print("📋 Use o .env.example como base:")
        print("   cp .env.example .env")
        print("   # Edite .env com suas credenciais reais")
        return

    # Configurar variáveis de ambiente para debug
    os.environ["DEBUG_MODE"] = "true"

    print("🐛 Modo DEBUG ativado!")
    print("👁️ O navegador será visível durante a execução")
    print("📝 Logs detalhados serão exibidos")
    print("⏸️ Em caso de erro, você poderá inspecionar a página")
    print()
    print("🚀 Iniciando execução...")
    print("-" * 50)

    # Executar o script principal
    try:
        import app.linkedin_poster
    except KeyboardInterrupt:
        print("\n⏹️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro durante execução: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script para executar o publicador LinkedIn localmente
"""
import subprocess
import sys
import os


def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import selenium
        from dotenv import load_dotenv

        print("✅ Dependências Python OK")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

    # Verificar browsers
    browsers = []
    if subprocess.run(["which", "firefox"], capture_output=True).returncode == 0:
        browsers.append("firefox")
    if (
        subprocess.run(["which", "chromium-browser"], capture_output=True).returncode
        == 0
    ):
        browsers.append("chromium")
    if subprocess.run(["which", "google-chrome"], capture_output=True).returncode == 0:
        browsers.append("chrome")

    if browsers:
        print(f"✅ Navegadores disponíveis: {', '.join(browsers)}")
    else:
        print("❌ Nenhum navegador compatível encontrado")
        print("Instale: sudo apt install firefox chromium-browser")
        return False

    return True


def run_publicador():
    """Executa o publicador"""
    if not os.path.exists(".env"):
        print("❌ Arquivo .env não encontrado!")
        print("Crie o arquivo .env com suas credenciais")
        return False

    if not check_dependencies():
        return False

    print("🚀 Executando publicador...")
    try:
        result = subprocess.run(
            [sys.executable, "app/linkedin_poster.py"], capture_output=False, text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")
        return False


if __name__ == "__main__":
    success = run_publicador()
    if not success:
        print("\n💡 Dica: Tente executar localmente sem Docker:")
        print("   python app/linkedin_poster.py")
        sys.exit(1)
    else:
        print("✅ Publicador executado com sucesso!")

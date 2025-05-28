#!/usr/bin/env python3
"""
Script de demonstração para testar o navegador sem fazer login real
"""
import os, time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

# === Carregar variáveis do .env ===
load_dotenv()
BROWSER = os.getenv("BROWSER", "firefox").lower()


def get_driver():
    """Inicializa o driver do navegador"""
    if BROWSER == "chromium" or BROWSER == "chrome":
        opts = webdriver.ChromeOptions()
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(options=opts)
    else:
        opts = webdriver.FirefoxOptions()
        opts.add_argument("--headless")
        opts.add_argument("--width=1920")
        opts.add_argument("--height=1080")
        return webdriver.Firefox(options=opts)


def test_browser():
    """Testa se o navegador está funcionando"""
    print(f"🔍 Testando navegador: {BROWSER}")
    driver = get_driver()
    try:
        # Acessar página do LinkedIn (sem fazer login)
        driver.get("https://www.linkedin.com")
        time.sleep(3)

        # Verificar se carregou
        title = driver.title
        print(f"✅ Página carregada: {title}")

        # Tentar encontrar o botão de login
        try:
            login_btn = driver.find_element(By.LINK_TEXT, "Entrar")
            print("✅ Botão de login encontrado")
        except:
            print("⚠️ Botão de login não encontrado (pode ser diferença de idioma)")

        print("✅ Teste do navegador concluído com sucesso!")

    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    test_browser()

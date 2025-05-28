#!/usr/bin/env python3
"""
Script para execução no Docker usando imagem oficial do Selenium
"""
import os, time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# === Carregar variáveis do .env ===
load_dotenv()
EMAIL = os.getenv("LINKEDIN_EMAIL")
PWD = os.getenv("LINKEDIN_PASSWORD")
TEXT = os.getenv("POST_TEXT")

print("🐳 Executando no Docker com Selenium Grid...")


def get_driver():
    """Configuração para Selenium Grid no container"""
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--remote-debugging-port=9222")

    # Tentar conectar ao Chrome local do Selenium Grid
    try:
        # Usar o Chrome já configurado na imagem selenium/standalone-chrome
        return webdriver.Chrome(options=opts)
    except Exception as e:
        print(f"❌ Erro ao conectar Chrome: {e}")
        # Fallback para remote driver se necessário
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

        return webdriver.Remote(
            command_executor="http://localhost:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.CHROME,
            options=opts,
        )


def login(drv):
    """Login no LinkedIn"""
    print("🔑 Fazendo login no LinkedIn...")
    drv.get("https://www.linkedin.com/login")
    time.sleep(3)

    drv.find_element(By.ID, "username").send_keys(EMAIL)
    drv.find_element(By.ID, "password").send_keys(PWD, Keys.RETURN)
    time.sleep(3)

    if "feed" not in drv.current_url:
        print("⚠️ Possível falha no login - verificando...")
    else:
        print("✅ Login realizado com sucesso")


def publish_post(drv, text):
    """Publica o post"""
    print("📝 Publicando post...")
    drv.get("https://www.linkedin.com/feed/")
    time.sleep(3)

    # Tentar encontrar botão de post
    try:
        drv.find_element(By.CLASS_NAME, "share-box-feed-entry__trigger").click()
        time.sleep(2)

        box = drv.find_element(By.CLASS_NAME, "ql-editor")
        box.click()
        box.send_keys(text)

        drv.find_element(By.XPATH, "//button[contains(.,'Publicar')]").click()
        time.sleep(3)
        print("✅ Post publicado!")

    except Exception as e:
        print(f"⚠️ Erro ao publicar: {e}")


if __name__ == "__main__":
    print("🚀 Iniciando automatizador LinkedIn no Docker...")

    driver = None
    try:
        driver = get_driver()
        print("✅ Driver iniciado com sucesso")

        if EMAIL and PWD and EMAIL != "seu_email@exemplo.com":
            login(driver)
            publish_post(driver, TEXT)
        else:
            print("⚠️ Credenciais não configuradas - executando apenas teste")
            driver.get("https://www.linkedin.com")
            print(f"✅ Página carregada: {driver.title}")

    except Exception as e:
        print(f"❌ Erro geral: {e}")
    finally:
        if driver:
            driver.quit()
        print("🏁 Execução finalizada")

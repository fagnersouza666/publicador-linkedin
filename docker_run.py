#!/usr/bin/env python3
"""
Script específico para execução no Docker usando Chromium
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

print("🐳 Executando no Docker com Chromium...")


def get_driver():
    """Força o uso do Chromium no Docker"""
    opts = webdriver.ChromeOptions()
    opts.binary_location = "/usr/bin/chromium-browser"
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-web-security")
    opts.add_argument("--disable-features=VizDisplayCompositor")

    return webdriver.Chrome(options=opts)


def login(drv):
    """Login no LinkedIn"""
    drv.get("https://www.linkedin.com/login")
    drv.find_element(By.ID, "username").send_keys(EMAIL)
    drv.find_element(By.ID, "password").send_keys(PWD, Keys.RETURN)
    time.sleep(3)
    assert "feed" in drv.current_url, "Falha no login"


def publish_post(drv, text):
    """Publica o post"""
    drv.get("https://www.linkedin.com/feed/")
    time.sleep(3)
    drv.find_element(By.CLASS_NAME, "share-box-feed-entry__trigger").click()
    time.sleep(2)
    box = drv.find_element(By.CLASS_NAME, "ql-editor")
    box.click()
    box.send_keys(text)
    drv.find_element(By.XPATH, "//button[contains(.,'Publicar')]").click()
    time.sleep(3)


if __name__ == "__main__":
    driver = get_driver()
    try:
        login(driver)
        publish_post(driver, TEXT)
        print("✅ Post publicado com sucesso!")
    except Exception as e:
        print("❌ Erro:", e)
    finally:
        driver.quit()

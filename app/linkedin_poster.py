import os, time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === Carregar variáveis do .env ===
load_dotenv()
EMAIL = os.getenv("LINKEDIN_EMAIL")
PWD = os.getenv("LINKEDIN_PASSWORD")
TEXT = os.getenv("POST_TEXT")
BROWSER = os.getenv("BROWSER", "firefox").lower()
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"  # Novo: modo debug


def log(message):
    """Log com timestamp para debug"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


# === Inicializa driver ===
def get_driver():
    log("🔧 Inicializando navegador...")

    if BROWSER == "chromium" or BROWSER == "chrome":
        opts = webdriver.ChromeOptions()

        # Se DEBUG_MODE = true, não usa headless
        if not DEBUG_MODE:
            opts.add_argument("--headless=new")
            log("👻 Modo headless ativado (invisível)")
        else:
            log("👁️ Modo visual ativado - você verá o navegador!")

        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        log("🌐 Usando Chrome/Chromium...")
        return webdriver.Chrome(options=opts)
    else:
        opts = webdriver.FirefoxOptions()
        opts.binary_location = "/usr/bin/firefox"

        # Se DEBUG_MODE = true, não usa headless
        if not DEBUG_MODE:
            opts.add_argument("--headless")
            log("👻 Modo headless ativado (invisível)")
        else:
            log("👁️ Modo visual ativado - você verá o navegador!")

        opts.add_argument("--width=1920")
        opts.add_argument("--height=1080")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        # Configurações específicas para container Docker
        opts.set_preference("dom.webdriver.enabled", False)
        opts.set_preference("useAutomationExtension", False)

        log("🦊 Usando Firefox...")
        return webdriver.Firefox(options=opts)


# === Login no LinkedIn ===
def login(drv):
    log("🔐 Iniciando processo de login...")

    log("📱 Acessando página de login do LinkedIn...")
    drv.get("https://www.linkedin.com/login")

    if DEBUG_MODE:
        log("⏳ Aguardando 3 segundos para você ver a página...")
        time.sleep(3)

    log("✍️ Preenchendo email...")
    username_field = drv.find_element(By.ID, "username")
    username_field.clear()
    username_field.send_keys(EMAIL)

    log("🔑 Preenchendo senha...")
    password_field = drv.find_element(By.ID, "password")
    password_field.clear()
    password_field.send_keys(PWD)

    if DEBUG_MODE:
        log("⏳ Aguardando 2 segundos antes de clicar em entrar...")
        time.sleep(2)

    log("🚀 Clicando no botão de login...")
    password_field.send_keys(Keys.RETURN)

    log("⏳ Aguardando resposta do LinkedIn...")
    time.sleep(5)

    current_url = drv.current_url
    log(f"📍 URL atual: {current_url}")

    # Verificações de login
    if "challenge" in current_url:
        log("🚨 ATENÇÃO: LinkedIn está pedindo verificação adicional!")
        log("📱 VERIFICAÇÃO NECESSÁRIA:")
        log("   1️⃣ Abra o app LinkedIn no seu celular")
        log("   2️⃣ Procure a notificação de login")
        log("   3️⃣ Toque em 'Yes' para confirmar")
        log("   4️⃣ OU clique 'Resend' no navegador")

        if DEBUG_MODE:
            log("⏸️ Aguardando você resolver a verificação...")
            log("💡 Dica: Mantenha esta janela aberta e resolva no celular")

            # Aguardar resolução da verificação
            while "challenge" in drv.current_url:
                try:
                    response = input(
                        "✅ Resolveu a verificação? (s/n/r=resend): "
                    ).lower()
                    if response == "s":
                        break
                    elif response == "r":
                        try:
                            resend_btn = drv.find_element(
                                By.XPATH,
                                "//button[contains(text(), 'Resend') or contains(text(), 'Reenviar')]",
                            )
                            resend_btn.click()
                            log(
                                "📤 Botão 'Resend' clicado! Verifique seu celular novamente."
                            )
                            time.sleep(3)
                        except:
                            log("⚠️ Botão 'Resend' não encontrado")
                    elif response == "n":
                        log(
                            "⏳ Aguardando... Digite 's' quando resolver ou 'r' para resend"
                        )

                    time.sleep(2)
                    current_url = drv.current_url
                    log(f"📍 URL atual: {current_url}")

                except KeyboardInterrupt:
                    log("⏹️ Processo interrompido pelo usuário")
                    raise Exception("Verificação cancelada pelo usuário")

            log("✅ Verificação resolvida! Continuando...")
        else:
            log("💡 Execute com 'python debug_local.py' para resolver interativamente")
            raise Exception(
                "Verificação adicional necessária - use modo debug para resolver"
            )

    elif "feed" in current_url:
        log("✅ Login realizado com sucesso!")
    elif "login" in current_url:
        log("❌ Login falhou - ainda na página de login")
        log("🔍 Verificando se há mensagens de erro...")
        try:
            error_element = drv.find_element(
                By.CSS_SELECTOR, ".alert--error, .form__label--error"
            )
            error_text = error_element.text
            log(f"❌ Erro encontrado: {error_text}")
        except:
            log("❌ Login falhou, mas nenhuma mensagem de erro específica encontrada")
        raise Exception(
            "Falha no login - credenciais incorretas ou verificação necessária"
        )
    else:
        log(f"⚠️ URL inesperada após login: {current_url}")
        if DEBUG_MODE:
            log("🔍 Verificando se precisa de ação manual...")
            input("⏸️ Pressione ENTER após verificar a página...")


# === Publica o post ===
def publish_post(drv, text):
    log("📝 Iniciando processo de publicação...")

    log("📰 Navegando para o feed...")
    drv.get("https://www.linkedin.com/feed/")
    time.sleep(3)

    log("🎯 Procurando botão 'Começar um post'...")
    try:
        # Tenta diferentes seletores possíveis
        start_post_selectors = [
            ".share-box-feed-entry__trigger",
            "[data-test-id='share-box-trigger']",
            ".artdeco-button--primary[aria-label*='post']",
            "button[aria-label*='Começar um post']",
        ]

        post_button = None
        for selector in start_post_selectors:
            try:
                post_button = drv.find_element(By.CSS_SELECTOR, selector)
                log(f"✅ Botão encontrado com seletor: {selector}")
                break
            except:
                continue

        if not post_button:
            raise Exception("Botão 'Começar um post' não encontrado")

        log("👆 Clicando no botão para começar post...")
        post_button.click()
        time.sleep(3)

        log("📝 Procurando área de texto...")
        text_area_selectors = [
            ".ql-editor",
            "[data-placeholder='Do que você gostaria de falar?']",
            ".share-creation-state__text-editor .ql-editor",
        ]

        text_area = None
        for selector in text_area_selectors:
            try:
                text_area = drv.find_element(By.CSS_SELECTOR, selector)
                log(f"✅ Área de texto encontrada com seletor: {selector}")
                break
            except:
                continue

        if not text_area:
            raise Exception("Área de texto não encontrada")

        log("✍️ Escrevendo o texto do post...")
        text_area.click()
        time.sleep(1)
        text_area.send_keys(text)

        if DEBUG_MODE:
            log("⏳ Aguardando 3 segundos para você ver o texto...")
            time.sleep(3)

        log("🎯 Procurando botão 'Publicar'...")
        publish_selectors = [
            "//button[contains(.,'Publicar')]",
            "//button[contains(.,'Post')]",
            "[data-test-id='share-actions-publish-button']",
        ]

        publish_button = None
        for selector in publish_selectors:
            try:
                if selector.startswith("//"):
                    publish_button = drv.find_element(By.XPATH, selector)
                else:
                    publish_button = drv.find_element(By.CSS_SELECTOR, selector)
                log(f"✅ Botão publicar encontrado!")
                break
            except:
                continue

        if not publish_button:
            raise Exception("Botão 'Publicar' não encontrado")

        log("🚀 Clicando em 'Publicar'...")
        publish_button.click()
        time.sleep(5)

        log("✅ Post publicado com sucesso!")

    except Exception as e:
        log(f"❌ Erro durante publicação: {e}")
        if DEBUG_MODE:
            log("🔍 Aguardando para você inspecionar a página...")
            input("⏸️ Pressione ENTER para continuar...")
        raise


# === Execução principal ===
if __name__ == "__main__":
    log("🚀 Iniciando Publicador LinkedIn...")

    if DEBUG_MODE:
        log("🐛 MODO DEBUG ATIVADO - Processo será visível!")
    else:
        log("👻 Modo headless - processo invisível")

    log(f"📧 Email: {EMAIL}")
    log(f"🌐 Navegador: {BROWSER}")
    log(f"📝 Texto: {TEXT[:50]}..." if len(TEXT) > 50 else f"📝 Texto: {TEXT}")

    driver = get_driver()
    try:
        login(driver)
        publish_post(driver, TEXT)
        log("🎉 Processo concluído com sucesso!")
    except Exception as e:
        log(f"💥 Erro geral: {e}")
        if DEBUG_MODE:
            log("🔍 Mantendo navegador aberto para debug...")
            input("⏸️ Pressione ENTER para fechar...")
    finally:
        log("🔚 Fechando navegador...")
        driver.quit()
        log("👋 Finalizado!")

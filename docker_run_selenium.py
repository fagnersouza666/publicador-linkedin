#!/usr/bin/env python3
"""
Script para execução no Docker usando imagem oficial do Selenium
"""
import os, time, uuid
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# === Carregar variáveis do .env ===
load_dotenv()
EMAIL = os.getenv("LINKEDIN_EMAIL")
PWD = os.getenv("LINKEDIN_PASSWORD")
TEXT = os.getenv("POST_TEXT")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

print("🐳 Executando no Docker com Selenium Grid...")


def log(message):
    """Log com timestamp para debug"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def wait_for_element(driver, selectors, timeout=5, method="css"):
    """
    Aguarda por um elemento usando múltiplos seletores
    """
    log(f"🔍 Aguardando elemento com {len(selectors)} seletores...")

    wait = WebDriverWait(driver, timeout)

    for i, selector in enumerate(selectors):
        try:
            # Verificar se a sessão ainda está ativa
            try:
                driver.current_url
            except:
                log("❌ Sessão do navegador perdida")
                return None

            if method == "mixed":
                # Detecta automaticamente se é XPath ou CSS
                if selector.startswith("//") or selector.startswith("("):
                    element = wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
            elif method == "xpath":
                element = wait.until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            else:
                element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )

            log(f"✅ Elemento encontrado com seletor {i+1}: {selector}")
            return element

        except TimeoutException:
            continue
        except Exception as e:
            log(f"⚠️ Erro ao procurar elemento com seletor {i+1}: {e}")
            continue

    log(f"❌ Nenhum elemento encontrado após {timeout}s")
    return None


def safe_click(driver, element, description="elemento"):
    """
    Clica em um elemento de forma segura, com fallback para JavaScript
    """
    try:
        # Scroll até o elemento
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        time.sleep(0.5)

        # Tentar clique normal
        element.click()
        log(f"✅ Clique normal no {description} bem-sucedido")
        return True

    except Exception as e:
        log(f"⚠️ Clique normal falhou no {description}: {e}")
        try:
            # Fallback para JavaScript
            driver.execute_script("arguments[0].click();", element)
            log(f"✅ Clique JavaScript no {description} bem-sucedido")
            return True
        except Exception as e2:
            log(f"❌ Clique JavaScript também falhou no {description}: {e2}")
            return False


def get_driver():
    """Configuração para Selenium Grid no container"""
    log("🔧 Inicializando navegador no Docker...")

    opts = webdriver.ChromeOptions()

    # Se DEBUG_MODE = true, não usa headless
    if not DEBUG_MODE:
        opts.add_argument("--headless")
        log("👻 Modo headless ativado (invisível)")
    else:
        log("👁️ Modo visual ativado - você verá o navegador!")

    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--remote-debugging-port=9222")

    # Argumentos únicos para evitar conflitos de user-data-dir
    unique_id = str(uuid.uuid4())[:8]
    opts.add_argument(f"--user-data-dir=/tmp/chrome-data-{unique_id}")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-plugins")
    opts.add_argument("--disable-images")
    opts.add_argument("--disable-web-security")

    # Melhorar performance
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--disable-renderer-backgrounding")

    # Tentar conectar ao Chrome local do Selenium Grid
    try:
        return webdriver.Chrome(options=opts)
    except Exception as e:
        log(f"❌ Erro ao conectar Chrome: {e}")
        # Fallback para remote driver se necessário
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

        return webdriver.Remote(
            command_executor="http://localhost:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.CHROME,
            options=opts,
        )


def login(drv):
    """Login no LinkedIn"""
    log("🔑 Fazendo login no LinkedIn...")
    drv.get("https://www.linkedin.com/login")
    time.sleep(3)

    log("✍️ Preenchendo credenciais...")
    drv.find_element(By.ID, "username").send_keys(EMAIL)
    drv.find_element(By.ID, "password").send_keys(PWD, Keys.RETURN)
    time.sleep(5)

    current_url = drv.current_url
    if "challenge" in current_url:
        log("🚨 ATENÇÃO: LinkedIn está pedindo verificação adicional!")
        raise Exception("Verificação adicional necessária")
    elif "feed" in current_url:
        log("✅ Login realizado com sucesso")
    else:
        log(f"⚠️ URL inesperada após login: {current_url}")
        raise Exception("Falha no login")


def publish_post(drv, text):
    """Publica o post com seletores robustos"""
    log("📝 Iniciando processo de publicação...")

    try:
        log("📰 Navegando para o feed...")
        drv.get("https://www.linkedin.com/feed/")
        time.sleep(5)

        log("🎯 Procurando botão 'Começar um post'...")

        # Lista expandida de seletores possíveis
        start_post_selectors = [
            # Seletores mais recentes (2024)
            "button[aria-label*='Start a post']",
            "button[aria-label*='Começar um post']",
            "button[aria-label*='Commencer un post']",
            "button[aria-label*='Empezar una publicación']",
            # Seletores por classe e data attributes
            ".share-box-feed-entry__trigger",
            "[data-test-id='share-box-trigger']",
            "[data-test-id='start-a-post-button']",
            ".feed-shared-update-v2__start-conversation-button",
            # Seletores por conteúdo de texto
            "//button[contains(text(), 'Start a post')]",
            "//button[contains(text(), 'Começar um post')]",
            # Seletores genéricos
            ".artdeco-button--primary[aria-label*='post']",
            "button.share-box-feed-entry__trigger",
            ".share-box-feed-entry button",
            # Novos seletores mais genéricos
            "//button[contains(@aria-label, 'post') or contains(@aria-label, 'Post')]",
            "button[data-tracking-control-name='public_post_feed-header_publisher-text-content']",
        ]

        # Usar função auxiliar para encontrar o botão
        post_button = wait_for_element(
            drv, start_post_selectors, timeout=8, method="mixed"
        )

        if not post_button:
            # Tentar estratégias alternativas
            log("🔄 Tentando estratégias alternativas...")

            # Verificar se há modal ou popup bloqueando
            try:
                close_buttons = drv.find_elements(
                    By.CSS_SELECTOR,
                    "[aria-label*='Close'], [aria-label*='Fechar'], .artdeco-modal__dismiss",
                )
                if close_buttons:
                    log("🚪 Fechando modal/popup que pode estar bloqueando...")
                    for btn in close_buttons:
                        safe_click(drv, btn, "botão fechar modal")
                    time.sleep(1)
            except:
                pass

            # Recarregar a página
            log("🔄 Recarregando página...")
            drv.refresh()
            time.sleep(3)

            # Tentar novamente
            post_button = wait_for_element(
                drv, start_post_selectors, timeout=5, method="mixed"
            )

            if not post_button:
                raise Exception(
                    "Botão 'Começar um post' não encontrado com nenhum seletor"
                )

        log("👆 Clicando no botão para começar post...")
        if not safe_click(drv, post_button, "botão começar post"):
            raise Exception("Falha ao clicar no botão de começar post")

        time.sleep(4)

        log("📝 Procurando área de texto do post...")
        text_area_selectors = [
            # Seletores mais recentes
            ".ql-editor[data-placeholder]",
            ".ql-editor p",
            "div[role='textbox']",
            # Seletores por placeholder
            "[data-placeholder*='What do you want to talk about']",
            "[data-placeholder*='Do que você gostaria de falar']",
            # Seletores clássicos
            ".ql-editor",
            ".share-creation-state__text-editor .ql-editor",
            # Fallbacks
            "div[contenteditable='true']",
            ".mentions-texteditor__content",
        ]

        # Usar função auxiliar para encontrar área de texto
        text_area = wait_for_element(drv, text_area_selectors, timeout=6, method="css")

        if not text_area:
            raise Exception("Área de texto não encontrada")

        log("✍️ Escrevendo o texto do post...")
        # Focar na área de texto
        if not safe_click(drv, text_area, "área de texto"):
            drv.execute_script("arguments[0].focus();", text_area)

        time.sleep(1)

        # Limpar e escrever texto
        try:
            text_area.send_keys(Keys.CONTROL + "a")
            time.sleep(0.5)
            text_area.send_keys(Keys.DELETE)
            time.sleep(0.5)
            text_area.send_keys(text)
            log(f"✅ Texto inserido: {text[:50]}...")
        except Exception as e:
            log(f"⚠️ Falha ao inserir texto normalmente: {e}")
            log("🔄 Tentando com JavaScript...")
            drv.execute_script(
                "arguments[0].innerHTML = arguments[1];", text_area, text
            )

        time.sleep(2)

        log("🎯 Procurando botão 'Publicar'...")
        publish_selectors = [
            # Por texto em diferentes idiomas
            "//button[contains(text(),'Post') and not(contains(text(),'postpone'))]",
            "//button[contains(text(),'Publicar')]",
            "//button[contains(text(),'Publier')]",
            # Por data attributes
            "[data-test-id='share-actions-publish-button']",
            "[data-test-id='post-button']",
            # Por aria-label
            "button[aria-label*='Post']",
            "button[aria-label*='Publicar']",
            # Por classes
            ".share-actions__primary-action",
            ".artdeco-button--primary[type='submit']",
            # Fallback genérico
            "button[type='submit']",
        ]

        # Usar função auxiliar para encontrar botão publicar
        publish_button = wait_for_element(
            drv, publish_selectors, timeout=5, method="mixed"
        )

        if not publish_button:
            raise Exception("Botão 'Publicar' não encontrado")

        # Verificar se botão está habilitado
        if not publish_button.is_enabled():
            log("⚠️ Botão publicar está desabilitado, aguardando...")
            time.sleep(3)

        log("🚀 Clicando em 'Publicar'...")
        if not safe_click(drv, publish_button, "botão publicar"):
            raise Exception("Falha ao clicar no botão publicar")

        time.sleep(5)
        log("✅ Post publicado com sucesso!")

    except Exception as e:
        log(f"❌ Erro durante publicação: {e}")
        raise


if __name__ == "__main__":
    log("🚀 Iniciando automatizador LinkedIn no Docker...")

    driver = None
    try:
        driver = get_driver()
        log("✅ Driver iniciado com sucesso")

        if EMAIL and PWD and EMAIL != "seu_email@exemplo.com":
            login(driver)
            publish_post(driver, TEXT)
        else:
            log("⚠️ Credenciais não configuradas - executando apenas teste")
            driver.get("https://www.linkedin.com")
            log(f"✅ Página carregada: {driver.title}")

    except Exception as e:
        log(f"❌ Erro geral: {e}")
    finally:
        if driver:
            driver.quit()
        log("🏁 Execução finalizada")

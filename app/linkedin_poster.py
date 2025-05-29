import os, time
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
BROWSER = os.getenv("BROWSER", "firefox").lower()
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"  # Novo: modo debug


def log(message):
    """Log com timestamp para debug"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def wait_for_element(driver, selectors, timeout=5, method="css"):
    """
    Aguarda por um elemento usando múltiplos seletores

    Args:
        driver: WebDriver instance
        selectors: Lista de seletores para tentar
        timeout: Tempo limite em segundos
        method: "css", "xpath" ou "mixed" (detecta automaticamente)

    Returns:
        WebElement encontrado ou None
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

    try:
        log("📰 Navegando para o feed...")
        drv.get("https://www.linkedin.com/feed/")
        time.sleep(3)  # Reduzido de 5 para 3

        if DEBUG_MODE:
            log("🔍 Página carregada, aguardando para inspeção...")
            time.sleep(1)  # Reduzido de 2 para 1

        log("🎯 Procurando botão 'Começar um post'...")

        # Lista expandida de seletores possíveis (LinkedIn muda frequentemente)
        start_post_selectors = [
            # Seletores mais recentes (2024)
            "button[aria-label*='Start a post']",
            "button[aria-label*='Começar um post']",
            "button[aria-label*='Commencer un post']",  # Francês
            "button[aria-label*='Empezar una publicación']",  # Espanhol
            # Seletores por classe e data attributes
            ".share-box-feed-entry__trigger",
            "[data-test-id='share-box-trigger']",
            "[data-test-id='start-a-post-button']",
            ".feed-shared-update-v2__start-conversation-button",
            # Seletores por conteúdo de texto
            "//button[contains(text(), 'Start a post')]",
            "//button[contains(text(), 'Começar um post')]",
            "//button[contains(text(), 'Commencer un post')]",
            "//button[contains(text(), 'Empezar una publicación')]",
            # Seletores genéricos
            ".artdeco-button--primary[aria-label*='post']",
            "button.share-box-feed-entry__trigger",
            ".share-box-feed-entry button",
            # Fallback para textarea diretamente
            ".share-box-feed-entry__top-bar",
            "div[data-test-id='share-box']",
            # Novos seletores mais genéricos
            "//button[contains(@aria-label, 'post') or contains(@aria-label, 'Post')]",
            "button[data-tracking-control-name='public_post_feed-header_publisher-text-content']",
        ]

        # Usar função auxiliar para encontrar o botão - timeout reduzido
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
                    time.sleep(1)  # Reduzido de 2 para 1
            except:
                pass

            # Recarregar a página
            log("🔄 Recarregando página...")
            drv.refresh()
            time.sleep(3)  # Reduzido de 5 para 3

            # Tentar novamente com timeout menor
            post_button = wait_for_element(
                drv, start_post_selectors, timeout=5, method="mixed"
            )

            if not post_button:
                # Screenshot para debug se DEBUG_MODE ativo
                if DEBUG_MODE:
                    log("📸 Tirando screenshot para debug...")
                    try:
                        drv.save_screenshot("/tmp/linkedin_debug.png")
                        log("📷 Screenshot salvo em /tmp/linkedin_debug.png")
                    except:
                        pass

                log("❌ Possíveis causas:")
                log("   1. LinkedIn mudou a interface")
                log("   2. Conta com restrições de publicação")
                log("   3. Região/idioma não suportado")
                log("   4. LinkedIn detectou automação")

                raise Exception(
                    "Botão 'Começar um post' não encontrado com nenhum seletor"
                )

        log("👆 Clicando no botão para começar post...")
        if not safe_click(drv, post_button, "botão começar post"):
            raise Exception("Falha ao clicar no botão de começar post")

        time.sleep(3)  # Reduzido de 4 para 3

        if DEBUG_MODE:
            log("⏳ Modal deve ter aberto, aguardando para inspeção...")
            time.sleep(1)  # Reduzido de 2 para 1

        log("📝 Procurando área de texto do post...")
        text_area_selectors = [
            # Seletores mais recentes
            ".ql-editor[data-placeholder]",
            ".ql-editor p",
            "div[role='textbox']",
            # Seletores por placeholder
            "[data-placeholder*='What do you want to talk about']",
            "[data-placeholder*='Do que você gostaria de falar']",
            "[data-placeholder*='De quoi voulez-vous parler']",
            "[data-placeholder*='¿De qué te gustaría hablar']",
            # Seletores clássicos
            ".ql-editor",
            ".share-creation-state__text-editor .ql-editor",
            ".share-creation-state__text-editor div[role='textbox']",
            # Fallbacks
            "div[contenteditable='true']",
            ".mentions-texteditor__content",
            # Seletores mais específicos
            ".editor-content .ql-editor",
            ".ql-container .ql-editor",
        ]

        # Usar função auxiliar para encontrar área de texto - timeout reduzido
        text_area = wait_for_element(drv, text_area_selectors, timeout=6, method="css")

        if not text_area:
            if DEBUG_MODE:
                log("📸 Tirando screenshot do modal para debug...")
                try:
                    drv.save_screenshot("/tmp/linkedin_modal_debug.png")
                    log("📷 Screenshot do modal salvo em /tmp/linkedin_modal_debug.png")
                except:
                    pass
            raise Exception("Área de texto não encontrada")

        log("✍️ Escrevendo o texto do post...")
        # Scroll até a área de texto
        drv.execute_script("arguments[0].scrollIntoView({block: 'center'});", text_area)
        time.sleep(0.5)  # Reduzido de 1 para 0.5

        # Focar na área de texto
        if not safe_click(drv, text_area, "área de texto"):
            log("⚠️ Falha ao clicar na área de texto, tentando foco direto...")
            drv.execute_script("arguments[0].focus();", text_area)

        time.sleep(0.5)  # Reduzido de 1 para 0.5

        # Limpar conteúdo existente e escrever texto
        try:
            text_area.send_keys(Keys.CONTROL + "a")
            time.sleep(0.3)  # Reduzido de 0.5 para 0.3
            text_area.send_keys(Keys.DELETE)
            time.sleep(0.3)  # Reduzido de 0.5 para 0.3
            text_area.send_keys(text)
            log(f"✅ Texto inserido: {text[:50]}...")
        except Exception as e:
            log(f"⚠️ Falha ao inserir texto normalmente: {e}")
            log("🔄 Tentando com JavaScript...")
            drv.execute_script(
                "arguments[0].innerHTML = arguments[1];", text_area, text
            )
            drv.execute_script(
                "arguments[0].textContent = arguments[1];", text_area, text
            )

        if DEBUG_MODE:
            log("⏳ Texto inserido, aguardando para verificação...")
            time.sleep(2)  # Reduzido de 3 para 2

        log("🎯 Procurando botão 'Publicar'...")
        publish_selectors = [
            # Por texto em diferentes idiomas
            "//button[contains(text(),'Post') and not(contains(text(),'postpone'))]",
            "//button[contains(text(),'Publicar')]",
            "//button[contains(text(),'Publier')]",
            # Por data attributes
            "[data-test-id='share-actions-publish-button']",
            "[data-test-id='post-button']",
            "button[data-test-id*='publish']",
            # Por aria-label
            "button[aria-label*='Post']",
            "button[aria-label*='Publicar']",
            # Por classes
            ".share-actions__primary-action",
            ".artdeco-button--primary[type='submit']",
            # Seletores mais específicos
            "button.share-actions__primary-action",
            "button[data-tracking-control-name*='publish']",
            # Fallback genérico
            "button[type='submit']",
        ]

        # Usar função auxiliar para encontrar botão publicar - timeout reduzido
        publish_button = wait_for_element(
            drv, publish_selectors, timeout=5, method="mixed"
        )

        if not publish_button:
            if DEBUG_MODE:
                log("📸 Tirando screenshot dos botões para debug...")
                try:
                    drv.save_screenshot("/tmp/linkedin_buttons_debug.png")
                    log(
                        "📷 Screenshot dos botões salvo em /tmp/linkedin_buttons_debug.png"
                    )
                except:
                    pass
            raise Exception("Botão 'Publicar' não encontrado")

        # Verificar se botão está habilitado
        if not publish_button.is_enabled():
            log("⚠️ Botão publicar está desabilitado, aguardando...")
            time.sleep(2)  # Reduzido de 3 para 2

            if not publish_button.is_enabled():
                log(
                    "❌ Botão ainda desabilitado. Verificando se texto foi inserido corretamente..."
                )
                if DEBUG_MODE:
                    try:
                        input("🔍 Pressione ENTER após verificar o texto na tela...")
                    except EOFError:
                        log("⚠️ Entrada não disponível no Docker, continuando...")

        log("🚀 Clicando em 'Publicar'...")
        if not safe_click(drv, publish_button, "botão publicar"):
            raise Exception("Falha ao clicar no botão publicar")

        time.sleep(3)  # Reduzido de 5 para 3

        # Verificar se foi publicado com sucesso
        log("✅ Comando de publicação enviado!")

        if DEBUG_MODE:
            log("🔍 Aguardando para verificar se foi publicado...")
            time.sleep(2)  # Reduzido de 3 para 2

            # Verificar se voltou ao feed
            try:
                current_url = drv.current_url
                if "feed" in current_url and "share" not in current_url:
                    log("✅ Voltou ao feed - publicação provavelmente bem-sucedida!")
                else:
                    log(f"⚠️ URL atual: {current_url}")
                    log("🔍 Verifique manualmente se foi publicado")
            except:
                log("⚠️ Não foi possível verificar URL final")

        log("✅ Post publicado com sucesso!")

    except Exception as e:
        log(f"❌ Erro durante publicação: {e}")

        if DEBUG_MODE:
            log("🔍 Erro detectado - mantendo navegador aberto para inspeção...")
            log("💡 Dicas para debug:")
            log("   1. Verifique se a página carregou completamente")
            log("   2. Verifique se não há pop-ups ou notificações bloqueando")
            log("   3. Verifique se o idioma da interface mudou")
            log("   4. Verifique se há atualizações na interface do LinkedIn")

            try:
                current_url = drv.current_url
                log(f"📍 URL atual: {current_url}")
                page_title = drv.title
                log(f"📋 Título da página: {page_title}")
            except:
                log("⚠️ Não foi possível obter informações da página (sessão perdida)")

            try:
                input("⏸️ Pressione ENTER para continuar após inspeção...")
            except EOFError:
                log(
                    "⚠️ Entrada não disponível no Docker, continuando automaticamente..."
                )
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
            try:
                input("⏸️ Pressione ENTER para fechar...")
            except EOFError:
                log("⚠️ Entrada não disponível no Docker, fechando automaticamente...")
    finally:
        log("🔚 Fechando navegador...")
        driver.quit()
        log("👋 Finalizado!")

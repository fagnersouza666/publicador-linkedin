#!/usr/bin/env python3
"""
Publicador Automático LinkedIn - Versão Enterprise
Funciona tanto localmente quanto no Docker com observabilidade completa
"""
import os
import time
import uuid
import logging
import csv
import json
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    InvalidSessionIdException,
)


# === Configurações de Observabilidade ===
class ObservabilityManager:
    """Gerenciador de observabilidade com logs CSV e alertas"""

    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        self.csv_log_file = os.path.join(log_dir, "linkedin_audit.csv")
        self.ensure_log_directory()
        self.ensure_csv_headers()

    def ensure_log_directory(self) -> None:
        """Garante que o diretório de logs existe"""
        os.makedirs(self.log_dir, exist_ok=True)

    def ensure_csv_headers(self) -> None:
        """Garante que o arquivo CSV tem cabeçalhos"""
        if not os.path.exists(self.csv_log_file):
            with open(self.csv_log_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "execution_id",
                        "action",
                        "success",
                        "post_text",
                        "current_url",
                        "error_type",
                        "error_msg",
                        "screenshot_path",
                        "duration_ms",
                    ]
                )

    def log_csv_event(
        self,
        execution_id: str,
        action: str,
        success: bool,
        post_text: str = "",
        current_url: str = "",
        error_type: str = "",
        error_msg: str = "",
        screenshot_path: str = "",
        duration_ms: int = 0,
    ) -> None:
        """Registra evento no log CSV para auditoria"""
        try:
            with open(self.csv_log_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        datetime.now().isoformat(),
                        execution_id,
                        action,
                        success,
                        post_text[:100] + "..." if len(post_text) > 100 else post_text,
                        current_url,
                        error_type,
                        error_msg[:200] + "..." if len(error_msg) > 200 else error_msg,
                        screenshot_path,
                        duration_ms,
                    ]
                )
        except Exception as e:
            logger.error(f"❌ Erro ao escrever log CSV: {e}")

    def send_telegram_alert(self, message: str) -> bool:
        """Envia alerta para Telegram"""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            logger.warning(
                "⚠️ Telegram não configurado (TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID)"
            )
            return False

        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": f"🚨 LinkedIn Bot Alert\n\n{message}",
                "parse_mode": "Markdown",
            }

            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Alerta Telegram enviado com sucesso")
                return True
            else:
                logger.error(
                    f"❌ Falha Telegram: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Erro ao enviar Telegram: {e}")
            return False

    def send_discord_alert(self, message: str) -> bool:
        """Envia alerta para Discord"""
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

        if not webhook_url:
            logger.warning("⚠️ Discord não configurado (DISCORD_WEBHOOK_URL)")
            return False

        try:
            payload = {
                "content": f"🚨 **LinkedIn Bot Alert**\n\n{message}",
                "username": "LinkedIn Bot",
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                logger.info("✅ Alerta Discord enviado com sucesso")
                return True
            else:
                logger.error(
                    f"❌ Falha Discord: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Erro ao enviar Discord: {e}")
            return False

    def send_alert(
        self, error_type: str, error_msg: str, url: str = "", screenshot: str = ""
    ) -> None:
        """Envia alertas para todos os canais configurados"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"""
**Erro**: {error_type}
**Mensagem**: {error_msg}
**URL**: {url}
**Screenshot**: {screenshot}
**Timestamp**: {timestamp}
        """.strip()

        # Tentar Telegram
        self.send_telegram_alert(message)

        # Tentar Discord
        self.send_discord_alert(message)


# === Configuração de Logging ===
def setup_logging() -> logging.Logger:
    """Configura sistema de logging profissional"""
    # Criar diretório de logs
    log_dir = "/logs" if os.path.exists("/.dockerenv") else "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Configurar logger
    logger = logging.getLogger("linkedin_poster")
    logger.setLevel(logging.INFO)

    # Evitar handlers duplicados
    if logger.handlers:
        return logger

    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        f"{log_dir}/poster.log", maxBytes=5 * 1024 * 1024, backupCount=3  # 5MB
    )
    file_handler.setLevel(logging.INFO)

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatadores
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter(
        "[%(asctime)s] %(message)s", datefmt="%H:%M:%S"
    )

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# === Carregar variáveis do .env ===
load_dotenv()
EMAIL = os.getenv("LINKEDIN_EMAIL")
PWD = os.getenv("LINKEDIN_PASSWORD")
TEXT = os.getenv("POST_TEXT")
BROWSER = os.getenv("BROWSER", "chromium").lower()
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Detectar se está rodando no Docker
DOCKER_MODE = (
    os.path.exists("/.dockerenv") or os.getenv("DOCKER_MODE", "false").lower() == "true"
)

# Configurar logging
logger = setup_logging()

# Configurar observabilidade
log_dir = "/logs" if DOCKER_MODE else "logs"
observability = ObservabilityManager(log_dir)

if DOCKER_MODE:
    logger.info("🐳 Executando no Docker com Selenium Grid...")
else:
    logger.info("💻 Executando localmente...")


def save_screenshot_on_error(driver: webdriver.Remote, error_msg: str) -> str:
    """Salva screenshot em caso de erro para debug"""
    try:
        log_dir = "/logs" if DOCKER_MODE else "logs"
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"{log_dir}/fail_{timestamp}.png"

        driver.save_screenshot(screenshot_path)
        logger.error(f"💥 Screenshot salvo: {screenshot_path}")
        logger.error(f"📄 Página atual: {driver.current_url}")
        logger.error(f"🔍 Título: {driver.title}")

        return screenshot_path

    except Exception as e:
        logger.error(f"❌ Falha ao salvar screenshot: {e}")
        return ""


def wait_for_element_smart(
    driver: webdriver.Remote,
    selectors: List[str],
    timeout: int = 10,
    method: str = "css",
) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    Aguarda por um elemento usando WebDriverWait e múltiplos seletores
    """
    logger.info(
        f"🔍 Aguardando elemento com {len(selectors)} seletores (timeout: {timeout}s)..."
    )

    wait = WebDriverWait(driver, timeout)

    for i, selector in enumerate(selectors):
        try:
            # Verificar se a sessão ainda está ativa
            try:
                driver.current_url
            except InvalidSessionIdException:
                logger.error("❌ Sessão do navegador perdida")
                return None

            if method == "mixed":
                # Detecta automaticamente se é XPath ou CSS
                if selector.startswith("//") or selector.startswith("("):
                    element = wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    element = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
            elif method == "xpath":
                element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            else:
                element = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )

            logger.info(f"✅ Elemento encontrado com seletor {i+1}: {selector}")
            return element

        except TimeoutException:
            logger.debug(f"⏱️ Timeout no seletor {i+1}: {selector}")
            continue
        except NoSuchElementException:
            logger.debug(f"🚫 Elemento não encontrado: {selector}")
            continue
        except WebDriverException as e:
            logger.warning(f"⚠️ Erro WebDriver no seletor {i+1}: {e}")
            continue

    logger.error(f"❌ Nenhum elemento encontrado após {timeout}s")
    return None


def safe_click(
    driver: webdriver.Remote,
    element: webdriver.remote.webelement.WebElement,
    description: str = "elemento",
) -> bool:
    """
    Clica em um elemento de forma segura, com fallback para JavaScript
    """
    try:
        # Aguardar elemento estar visível e clicável
        wait = WebDriverWait(driver, 5)
        wait.until(EC.element_to_be_clickable(element))

        # Scroll até o elemento
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )

        # Aguardar um pouco após scroll
        wait.until(EC.element_to_be_clickable(element))

        # Tentar clique normal
        element.click()
        logger.info(f"✅ Clique normal no {description} bem-sucedido")
        return True

    except TimeoutException:
        logger.warning(f"⏱️ Timeout no clique do {description}")
        return False
    except WebDriverException as e:
        logger.warning(f"⚠️ Clique normal falhou no {description}: {e}")
        try:
            # Fallback para JavaScript
            driver.execute_script("arguments[0].click();", element)
            logger.info(f"✅ Clique JavaScript no {description} bem-sucedido")
            return True
        except WebDriverException as e2:
            logger.error(f"❌ Clique JavaScript também falhou no {description}: {e2}")
            return False


def get_driver() -> webdriver.Remote:
    """Configuração unificada do navegador para Docker e local"""
    if DOCKER_MODE:
        logger.info("🔧 Inicializando navegador no Docker...")
        opts = webdriver.ChromeOptions()

        # Se DEBUG_MODE = true, não usa headless
        if not DEBUG_MODE:
            opts.add_argument("--headless")
            logger.info("👻 Modo headless ativado (invisível)")
        else:
            logger.info("👁️ Modo visual ativado - você verá o navegador!")

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
        except WebDriverException as e:
            logger.error(f"❌ Erro ao conectar Chrome: {e}")
            # Fallback para remote driver se necessário
            from selenium.webdriver.common.desired_capabilities import (
                DesiredCapabilities,
            )

            return webdriver.Remote(
                command_executor="http://localhost:4444/wd/hub",
                desired_capabilities=DesiredCapabilities.CHROME,
                options=opts,
            )
    else:
        logger.info("🔧 Inicializando navegador localmente...")

        if BROWSER == "firefox":
            from selenium.webdriver.firefox.options import Options as FirefoxOptions

            opts = FirefoxOptions()

            if not DEBUG_MODE:
                opts.add_argument("--headless")
                logger.info("👻 Firefox modo headless ativado")
            else:
                logger.info("👁️ Firefox modo visual ativado")

            opts.add_argument("--window-size=1920,1080")
            return webdriver.Firefox(options=opts)

        else:  # chromium/chrome
            opts = webdriver.ChromeOptions()

            if not DEBUG_MODE:
                opts.add_argument("--headless")
                logger.info("👻 Chrome modo headless ativado")
            else:
                logger.info("👁️ Chrome modo visual ativado")

            opts.add_argument("--window-size=1920,1080")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")

            # ID único para evitar conflitos
            unique_id = str(uuid.uuid4())[:8]
            opts.add_argument(f"--user-data-dir=/tmp/chrome-data-{unique_id}")

            return webdriver.Chrome(options=opts)


def login(driver: webdriver.Remote, execution_id: str) -> None:
    """Login no LinkedIn com validação robusta e observabilidade"""
    start_time = time.time()
    logger.info("🔑 Fazendo login no LinkedIn...")

    try:
        driver.get("https://www.linkedin.com/login")

        # Aguardar página carregar
        wait = WebDriverWait(driver, 10)

        # Aguardar campos de login aparecerem
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))

        logger.info("✍️ Preenchendo credenciais...")
        username_field.clear()
        username_field.send_keys(EMAIL)

        password_field.clear()
        password_field.send_keys(PWD)
        password_field.send_keys(Keys.RETURN)

        # Aguardar resposta do login
        wait.until(lambda driver: "login" not in driver.current_url.lower())

        current_url = driver.current_url
        duration_ms = int((time.time() - start_time) * 1000)

        if "challenge" in current_url:
            error_msg = "LinkedIn está pedindo verificação adicional"
            logger.error(f"🚨 ATENÇÃO: {error_msg}")
            screenshot_path = save_screenshot_on_error(driver, error_msg)

            # Log CSV
            observability.log_csv_event(
                execution_id,
                "login",
                False,
                "",
                current_url,
                "VerificationRequired",
                error_msg,
                screenshot_path,
                duration_ms,
            )

            # Enviar alerta
            observability.send_alert(
                "Verificação Adicional", error_msg, current_url, screenshot_path
            )

            raise Exception(error_msg)

        elif "feed" in current_url:
            logger.info("✅ Login realizado com sucesso")

            # Log CSV de sucesso
            observability.log_csv_event(
                execution_id, "login", True, "", current_url, "", "", "", duration_ms
            )

        else:
            logger.warning(f"⚠️ URL inesperada após login: {current_url}")
            if "linkedin.com" in current_url and "login" not in current_url:
                logger.info("✅ Login aparenta ter sido bem-sucedido")

                # Log CSV de sucesso com warning
                observability.log_csv_event(
                    execution_id,
                    "login",
                    True,
                    "",
                    current_url,
                    "UnexpectedURL",
                    f"URL inesperada: {current_url}",
                    "",
                    duration_ms,
                )
            else:
                error_msg = "Falha no login"
                screenshot_path = save_screenshot_on_error(driver, error_msg)

                # Log CSV de falha
                observability.log_csv_event(
                    execution_id,
                    "login",
                    False,
                    "",
                    current_url,
                    "LoginFailed",
                    error_msg,
                    screenshot_path,
                    duration_ms,
                )

                # Enviar alerta
                observability.send_alert(
                    "Falha no Login", error_msg, current_url, screenshot_path
                )

                raise Exception(error_msg)

    except TimeoutException as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_msg = f"Timeout durante login: {e}"
        logger.error(f"⏱️ {error_msg}")
        screenshot_path = save_screenshot_on_error(driver, error_msg)

        # Log CSV
        observability.log_csv_event(
            execution_id,
            "login",
            False,
            "",
            driver.current_url,
            "TimeoutException",
            str(e),
            screenshot_path,
            duration_ms,
        )

        # Enviar alerta
        observability.send_alert(
            "Timeout no Login", str(e), driver.current_url, screenshot_path
        )

        raise
    except NoSuchElementException as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_msg = f"Elemento de login não encontrado: {e}"
        logger.error(f"🚫 {error_msg}")
        screenshot_path = save_screenshot_on_error(driver, error_msg)

        # Log CSV
        observability.log_csv_event(
            execution_id,
            "login",
            False,
            "",
            driver.current_url,
            "NoSuchElementException",
            str(e),
            screenshot_path,
            duration_ms,
        )

        # Enviar alerta
        observability.send_alert(
            "Elemento Não Encontrado", str(e), driver.current_url, screenshot_path
        )

        raise
    except WebDriverException as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_msg = f"Erro do WebDriver durante login: {e}"
        logger.error(f"❌ {error_msg}")
        screenshot_path = save_screenshot_on_error(driver, error_msg)

        # Log CSV
        observability.log_csv_event(
            execution_id,
            "login",
            False,
            "",
            driver.current_url,
            "WebDriverException",
            str(e),
            screenshot_path,
            duration_ms,
        )

        # Enviar alerta
        observability.send_alert(
            "Erro WebDriver", str(e), driver.current_url, screenshot_path
        )

        raise


def publish_post(driver: webdriver.Remote, text: str, execution_id: str) -> None:
    """Publica o post com seletores robustos, validação completa e observabilidade"""
    start_time = time.time()
    logger.info("📝 Iniciando processo de publicação...")

    try:
        logger.info("📰 Navegando para o feed...")
        driver.get("https://www.linkedin.com/feed/")

        # Aguardar página carregar completamente
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        logger.info("🎯 Procurando botão 'Começar um post'...")

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
        post_button = wait_for_element_smart(
            driver, start_post_selectors, timeout=15, method="mixed"
        )

        if not post_button:
            # Tentar estratégias alternativas
            logger.info("🔄 Tentando estratégias alternativas...")

            # Verificar se há modal ou popup bloqueando
            try:
                close_buttons = driver.find_elements(
                    By.CSS_SELECTOR,
                    "[aria-label*='Close'], [aria-label*='Fechar'], .artdeco-modal__dismiss",
                )
                if close_buttons:
                    logger.info("🚪 Fechando modal/popup que pode estar bloqueando...")
                    for btn in close_buttons:
                        safe_click(driver, btn, "botão fechar modal")

                    # Aguardar após fechar modals
                    WebDriverWait(driver, 3).until(EC.staleness_of(close_buttons[0]))
            except (TimeoutException, NoSuchElementException):
                pass

            # Recarregar a página
            logger.info("🔄 Recarregando página...")
            driver.refresh()
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Tentar novamente
            post_button = wait_for_element_smart(
                driver, start_post_selectors, timeout=10, method="mixed"
            )

            if not post_button:
                error_msg = "Botão 'Começar um post' não encontrado com nenhum seletor"
                screenshot_path = save_screenshot_on_error(driver, error_msg)
                duration_ms = int((time.time() - start_time) * 1000)

                # Log CSV
                observability.log_csv_event(
                    execution_id,
                    "publish_post",
                    False,
                    text,
                    driver.current_url,
                    "NoSuchElementException",
                    error_msg,
                    screenshot_path,
                    duration_ms,
                )

                # Enviar alerta
                observability.send_alert(
                    "Elemento Não Encontrado",
                    error_msg,
                    driver.current_url,
                    screenshot_path,
                )

                raise NoSuchElementException(error_msg)

        logger.info("👆 Clicando no botão para começar post...")
        if not safe_click(driver, post_button, "botão começar post"):
            error_msg = "Falha ao clicar no botão de começar post"
            screenshot_path = save_screenshot_on_error(driver, error_msg)
            duration_ms = int((time.time() - start_time) * 1000)

            # Log CSV
            observability.log_csv_event(
                execution_id,
                "publish_post",
                False,
                text,
                driver.current_url,
                "WebDriverException",
                error_msg,
                screenshot_path,
                duration_ms,
            )

            # Enviar alerta
            observability.send_alert(
                "Erro ao Clicar", error_msg, driver.current_url, screenshot_path
            )

            raise WebDriverException(error_msg)

        # Aguardar modal de criação de post aparecer
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".share-creation-state, .ql-editor")
            )
        )

        logger.info("📝 Procurando área de texto do post...")
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
        text_area = wait_for_element_smart(
            driver, text_area_selectors, timeout=10, method="css"
        )

        if not text_area:
            error_msg = "Área de texto não encontrada"
            screenshot_path = save_screenshot_on_error(driver, error_msg)
            duration_ms = int((time.time() - start_time) * 1000)

            # Log CSV
            observability.log_csv_event(
                execution_id,
                "publish_post",
                False,
                text,
                driver.current_url,
                "NoSuchElementException",
                error_msg,
                screenshot_path,
                duration_ms,
            )

            # Enviar alerta
            observability.send_alert(
                "Área de Texto Não Encontrada",
                error_msg,
                driver.current_url,
                screenshot_path,
            )

            raise NoSuchElementException(error_msg)

        logger.info("✍️ Escrevendo o texto do post...")

        # Focar na área de texto e aguardar estar pronta
        if not safe_click(driver, text_area, "área de texto"):
            driver.execute_script("arguments[0].focus();", text_area)

        # Aguardar área estar focada
        wait.until(lambda d: d.switch_to.active_element == text_area)

        # Limpar e escrever texto
        try:
            text_area.send_keys(Keys.CONTROL + "a")
            WebDriverWait(driver, 2).until(lambda d: True)  # Pequena pausa
            text_area.send_keys(Keys.DELETE)
            WebDriverWait(driver, 2).until(lambda d: True)  # Pequena pausa
            text_area.send_keys(text)
            logger.info(f"✅ Texto inserido: {text[:50]}...")
        except WebDriverException as e:
            logger.warning(f"⚠️ Falha ao inserir texto normalmente: {e}")
            logger.info("🔄 Tentando com JavaScript...")
            driver.execute_script(
                "arguments[0].innerHTML = arguments[1];", text_area, text
            )

        # Aguardar texto ser processado
        WebDriverWait(driver, 5).until(
            lambda d: len(text_area.text.strip()) > 0
            or len(text_area.get_attribute("innerHTML")) > 10
        )

        logger.info("🎯 Procurando botão 'Publicar'...")
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
        publish_button = wait_for_element_smart(
            driver, publish_selectors, timeout=10, method="mixed"
        )

        if not publish_button:
            error_msg = "Botão 'Publicar' não encontrado"
            screenshot_path = save_screenshot_on_error(driver, error_msg)
            duration_ms = int((time.time() - start_time) * 1000)

            # Log CSV
            observability.log_csv_event(
                execution_id,
                "publish_post",
                False,
                text,
                driver.current_url,
                "NoSuchElementException",
                error_msg,
                screenshot_path,
                duration_ms,
            )

            # Enviar alerta
            observability.send_alert(
                "Botão Publicar Não Encontrado",
                error_msg,
                driver.current_url,
                screenshot_path,
            )

            raise NoSuchElementException(error_msg)

        # Verificar se botão está habilitado
        wait.until(lambda d: publish_button.is_enabled())

        logger.info("🚀 Clicando em 'Publicar'...")
        if not safe_click(driver, publish_button, "botão publicar"):
            error_msg = "Falha ao clicar no botão publicar"
            screenshot_path = save_screenshot_on_error(driver, error_msg)
            duration_ms = int((time.time() - start_time) * 1000)

            # Log CSV
            observability.log_csv_event(
                execution_id,
                "publish_post",
                False,
                text,
                driver.current_url,
                "WebDriverException",
                error_msg,
                screenshot_path,
                duration_ms,
            )

            # Enviar alerta
            observability.send_alert(
                "Erro ao Publicar", error_msg, driver.current_url, screenshot_path
            )

            raise WebDriverException(error_msg)

        # Aguardar confirmação de publicação
        try:
            wait.until(
                EC.any_of(
                    EC.url_contains("feed"),
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-test-id='post-success']")
                    ),
                )
            )
            logger.info("✅ Post publicado com sucesso!")

            duration_ms = int((time.time() - start_time) * 1000)

            # Log CSV de sucesso
            observability.log_csv_event(
                execution_id,
                "publish_post",
                True,
                text,
                driver.current_url,
                "",
                "",
                "",
                duration_ms,
            )

        except TimeoutException:
            logger.warning("⚠️ Timeout aguardando confirmação, mas comando foi enviado")
            logger.info("✅ Post provavelmente publicado com sucesso!")

            duration_ms = int((time.time() - start_time) * 1000)

            # Log CSV com warning
            observability.log_csv_event(
                execution_id,
                "publish_post",
                True,
                text,
                driver.current_url,
                "TimeoutConfirmation",
                "Timeout na confirmação mas comando enviado",
                "",
                duration_ms,
            )

    except TimeoutException as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_msg = f"Timeout durante publicação: {e}"
        logger.error(f"⏱️ {error_msg}")
        screenshot_path = save_screenshot_on_error(driver, error_msg)

        # Log CSV
        observability.log_csv_event(
            execution_id,
            "publish_post",
            False,
            text,
            driver.current_url,
            "TimeoutException",
            str(e),
            screenshot_path,
            duration_ms,
        )

        # Enviar alerta
        observability.send_alert(
            "Timeout na Publicação", str(e), driver.current_url, screenshot_path
        )

        raise
    except NoSuchElementException as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_msg = f"Elemento não encontrado durante publicação: {e}"
        logger.error(f"🚫 {error_msg}")
        screenshot_path = save_screenshot_on_error(driver, error_msg)

        # Log CSV
        observability.log_csv_event(
            execution_id,
            "publish_post",
            False,
            text,
            driver.current_url,
            "NoSuchElementException",
            str(e),
            screenshot_path,
            duration_ms,
        )

        # Enviar alerta
        observability.send_alert(
            "Elemento Não Encontrado", str(e), driver.current_url, screenshot_path
        )

        raise
    except WebDriverException as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_msg = f"Erro WebDriver durante publicação: {e}"
        logger.error(f"❌ {error_msg}")
        screenshot_path = save_screenshot_on_error(driver, error_msg)

        # Log CSV
        observability.log_csv_event(
            execution_id,
            "publish_post",
            False,
            text,
            driver.current_url,
            "WebDriverException",
            str(e),
            screenshot_path,
            duration_ms,
        )

        # Enviar alerta
        observability.send_alert(
            "Erro WebDriver", str(e), driver.current_url, screenshot_path
        )

        raise


if __name__ == "__main__":
    execution_id = str(uuid.uuid4())
    start_time = time.time()
    logger.info(f"🚀 Iniciando automatizador LinkedIn [ID: {execution_id}]")

    driver = None
    try:
        # Log CSV de início
        observability.log_csv_event(
            execution_id, "start", True, TEXT or "", "", "", "", "", 0
        )

        driver = get_driver()
        logger.info("✅ Driver iniciado com sucesso")

        if EMAIL and PWD and EMAIL != "seu_email@exemplo.com":
            login(driver, execution_id)
            publish_post(driver, TEXT, execution_id)

            # Log CSV de sucesso total
            total_duration = int((time.time() - start_time) * 1000)
            observability.log_csv_event(
                execution_id,
                "complete",
                True,
                TEXT,
                driver.current_url,
                "",
                "",
                "",
                total_duration,
            )
        else:
            logger.info("⚠️ Credenciais não configuradas - executando apenas teste")
            driver.get("https://www.linkedin.com")
            logger.info(f"✅ Página carregada: {driver.title}")

            # Log CSV de teste
            observability.log_csv_event(
                execution_id, "test", True, "", driver.current_url, "", "", "", 0
            )

    except Exception as e:
        total_duration = int((time.time() - start_time) * 1000)
        error_msg = f"Erro geral: {e}"
        logger.error(f"❌ {error_msg}")

        current_url = ""
        if driver:
            try:
                current_url = driver.current_url
            except:
                pass

        # Log CSV de erro geral
        observability.log_csv_event(
            execution_id,
            "error",
            False,
            TEXT or "",
            current_url,
            type(e).__name__,
            str(e),
            "",
            total_duration,
        )

        # Enviar alerta de erro geral
        observability.send_alert("Erro Geral", str(e), current_url)

    finally:
        if driver:
            driver.quit()
        logger.info("🏁 Execução finalizada")

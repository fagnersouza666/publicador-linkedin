#!/usr/bin/env python3
"""
Teste de navegadores: Chromium, Firefox e Chrome
"""
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def test_chromium():
    print("🔄 Testando Chromium...")
    try:
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Detectar caminho do Chromium
        for chromium_path in [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]:
            if os.path.exists(chromium_path):
                options.binary_location = chromium_path
                print(f"✅ Chromium encontrado em: {chromium_path}")
                break

        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        print(f"✅ Chromium funcionando! Título: {driver.title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ Chromium falhou: {e}")
        return False


def test_firefox():
    print("🔄 Testando Firefox...")
    try:
        options = FirefoxOptions()
        options.add_argument("--headless")

        driver = webdriver.Firefox(options=options)
        driver.get("https://www.google.com")
        print(f"✅ Firefox funcionando! Título: {driver.title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ Firefox falhou: {e}")
        return False


def test_chrome():
    print("🔄 Testando Google Chrome...")
    try:
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Usar o binário real do Chrome
        options.binary_location = "/opt/google/chrome/chrome"
        service = ChromeService("/usr/bin/chromedriver")

        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.google.com")
        print(f"✅ Chrome funcionando! Título: {driver.title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ Chrome falhou: {e}")
        return False


def main():
    print("🧪 Testando navegadores disponíveis...")
    print("=" * 50)

    results = {}

    # Testar Chromium (preferido)
    results["chromium"] = test_chromium()

    # Testar Firefox
    results["firefox"] = test_firefox()

    # Testar Chrome
    results["chrome"] = test_chrome()

    print("\n📊 Resultados dos testes:")
    print("=" * 50)

    working_browsers = []
    for browser, success in results.items():
        status = "✅ FUNCIONANDO" if success else "❌ COM PROBLEMAS"
        print(f"{browser.capitalize():<12}: {status}")
        if success:
            working_browsers.append(browser)

    print(f"\n🎯 Navegadores funcionando: {len(working_browsers)}/{len(results)}")

    if working_browsers:
        recommended = working_browsers[0]  # Primeiro que funciona
        print(f"🌟 Recomendado: {recommended}")
        print(f"\n📝 Para usar {recommended}, configure no .env:")
        print(f"BROWSER={recommended}")

        # Informações adicionais
        print(f"\n💡 Vantagens por navegador:")
        if "chromium" in working_browsers:
            print("- Chromium: Leve, open source, ideal para Docker")
        if "firefox" in working_browsers:
            print("- Firefox: Estável, suporte completo ao Selenium")
        if "chrome" in working_browsers:
            print("- Chrome: Funcionalidade completa, melhor compatibilidade")
    else:
        print("💥 Nenhum navegador está funcionando!")
        print("\n🔧 Sugestões:")
        print("- Instale Chromium: sudo apt-get install chromium-browser")
        print("- Instale Firefox: sudo apt-get install firefox")
        print("- Execute ./install.sh para configuração automática")

    return len(working_browsers) > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

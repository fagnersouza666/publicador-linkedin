#!/usr/bin/env python3
"""
Teste do Sistema de Revisão de Conteúdo v2.6.1
Verificar integração ContentReviewer + TelegramBot
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


def test_content_reviewer():
    """Testar módulo ContentReviewer isoladamente"""
    print("🧪 Testando ContentReviewer...")

    # Verificar se OpenAI está configurado
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY não configurado - skipping teste IA")
        return False

    try:
        from app.content_reviewer import ContentReviewer

        reviewer = ContentReviewer()

        # Conteúdo de teste
        test_content = """
🚀 A revolução da inteligência artificial na educação está transformando completamente a forma como aprendemos e ensinamos. 

As novas tecnologias permitem:
• Personalização do aprendizado para cada aluno
• Feedback em tempo real sobre o progresso
• Identificação de dificuldades específicas
• Conteúdo adaptativo baseado no desempenho

Os professores agora podem focar no que realmente importa: inspirar, orientar e desenvolver habilidades críticas e criativas nos estudantes.

O futuro da educação já chegou! 🎓

#educacao #inteligenciaartificial #tecnologia #futuro #inovacao
"""

        print("📝 Testando revisão de conteúdo...")
        review = reviewer.review_content(test_content, "IA na Educação")

        print("✅ Revisão completa!")
        print(f"📊 Status: {review.get('final_recommendation', 'N/A')}")
        print(f"🎯 Confiança: {review.get('confidence_score', 0):.0%}")
        print(f"📏 Caracteres: {review.get('char_count', 0)}")

        # Testar formatação para Telegram
        formatted = reviewer.format_review_for_telegram(review, test_content)
        print("\n📱 Formato Telegram:")
        print(formatted[:200] + "..." if len(formatted) > 200 else formatted)

        return True

    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False


def test_file_structure():
    """Verificar estrutura de arquivos necessária"""
    print("\n📁 Verificando estrutura de arquivos...")

    required_files = [
        "app/content_reviewer.py",
        "app/telegram_bot.py",
        "app/post_processor.py",
        "app/html_parser.py",
        "requirements.txt",
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("❌ Arquivos ausentes:")
        for file in missing_files:
            print(f"   • {file}")
        return False
    else:
        print("✅ Todos os arquivos necessários presentes")
        return True


def test_directories():
    """Verificar diretórios de produção"""
    print("\n📂 Verificando diretórios de produção...")

    required_dirs = ["posts", "posts/pendentes", "posts/enviados", "posts/logs"]

    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"📁 Criando diretório: {directory}")
            os.makedirs(directory, exist_ok=True)
        else:
            print(f"✅ Diretório existe: {directory}")

    return True


def test_dependencies():
    """Verificar dependências Python"""
    print("\n📦 Verificando dependências...")

    dependencies = [
        ("openai", "OpenAI API"),
        ("telegram", "Python Telegram Bot"),
        ("beautifulsoup4", "HTML Parser"),
        ("selenium", "LinkedIn Automation"),
        ("dotenv", "Environment Variables"),
    ]

    missing_deps = []
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            missing_deps.append(name)
            print(f"❌ {name}")

    if missing_deps:
        print(f"\n💡 Instalar dependências ausentes:")
        print("pip install -r requirements.txt")
        return False

    return True


def test_config():
    """Verificar configurações essenciais"""
    print("\n🔧 Verificando configurações...")

    configs = [
        ("TELEGRAM_BOT_TOKEN", "Token do Bot Telegram"),
        ("OPENAI_API_KEY", "Chave da API OpenAI"),
        ("LINKEDIN_EMAIL", "Email LinkedIn"),
        ("LINKEDIN_PASSWORD", "Senha LinkedIn"),
    ]

    missing_configs = []
    for env_var, name in configs:
        if os.getenv(env_var):
            print(f"✅ {name}")
        else:
            missing_configs.append(name)
            print(f"❌ {name}")

    if missing_configs:
        print(f"\n💡 Configure no arquivo .env:")
        for config in missing_configs:
            print(f"   • {config}")
        return False

    return True


def main():
    """Executar todos os testes"""
    print("🚀 Teste do Sistema de Revisão v2.6.1")
    print("=" * 50)

    tests = [
        ("Estrutura de Arquivos", test_file_structure),
        ("Diretórios de Produção", test_directories),
        ("Dependências Python", test_dependencies),
        ("Configurações", test_config),
        ("ContentReviewer", test_content_reviewer),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))

    # Resumo dos resultados
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1

    total = len(results)
    print(f"\n🎯 Taxa de sucesso: {passed}/{total} ({passed*100//total}%)")

    if passed == total:
        print("\n🎉 Todos os testes passaram! Sistema pronto para uso.")
        print("\n🚀 Para iniciar o bot:")
        print("./iniciar_telegram_bot.sh")
    else:
        print(f"\n⚠️ {total-passed} teste(s) falharam. Verifique as configurações.")

    return passed == total


if __name__ == "__main__":
    main()

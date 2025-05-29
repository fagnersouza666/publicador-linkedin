#!/usr/bin/env python3
"""
Script de teste para o pipeline Telegram → GPT → LinkedIn
Testa cada componente individualmente
"""
import os
import asyncio
from pathlib import Path


# Teste do processador
async def test_post_processor():
    """Testar o processador de posts"""
    print("🧪 Testando Post Processor...")

    # Criar arquivo HTML de teste
    test_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Teste</title></head>
    <body>
        <main>
            <h1>Inteligência Artificial na Educação</h1>
            <p>A inteligência artificial está transformando a forma como aprendemos. 
            Novas tecnologias permitem personalização do ensino, adaptando-se ao ritmo 
            de cada estudante. Ferramentas como chatbots educacionais e sistemas de 
            tutoria inteligente estão revolucionando as salas de aula.</p>
            
            <p>Benefícios incluem:</p>
            <ul>
                <li>Aprendizagem personalizada</li>
                <li>Feedback instantâneo</li>
                <li>Identificação de lacunas de conhecimento</li>
                <li>Automação de tarefas administrativas</li>
            </ul>
            
            <p>O futuro da educação será uma combinação harmoniosa entre 
            tecnologia e interação humana, criando experiências de aprendizagem 
            mais eficazes e envolventes.</p>
        </main>
    </body>
    </html>
    """

    # Salvar arquivo de teste
    test_file = "posts/test_article.html"
    os.makedirs("posts", exist_ok=True)

    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_html)

    print(f"📄 Arquivo de teste criado: {test_file}")

    try:
        from app.post_processor import PostProcessor

        processor = PostProcessor()

        # Testar extração de texto
        print("1️⃣ Testando extração de texto...")
        text = processor.extract_text_from_html(test_file)
        print(f"   ✅ Texto extraído: {len(text)} caracteres")
        print(f"   📝 Preview: {text[:100]}...")

        # Testar processamento GPT
        print("2️⃣ Testando processamento GPT...")
        if not os.getenv("OPENAI_API_KEY"):
            print("   ⚠️ OPENAI_API_KEY não configurada - pulando teste GPT")
            return

        processed = await processor.process_html_file(test_file)
        print(f"   ✅ Conteúdo processado: {len(processed)} caracteres")
        print(f"   📝 Resultado:")
        print("   " + "=" * 50)
        print("   " + processed.replace("\n", "\n   "))
        print("   " + "=" * 50)

        # Testar validação
        validation = processor.validate_content(processed)
        print(f"3️⃣ Validação: {'✅ Passou' if validation['valid'] else '❌ Falhou'}")
        if validation["issues"]:
            print(f"   ⚠️ Issues: {', '.join(validation['issues'])}")

        print(f"   📊 Stats: {validation['stats']}")

    except Exception as e:
        print(f"❌ Erro no teste: {e}")


def test_telegram_config():
    """Testar configurações do Telegram"""
    print("🧪 Testando configuração Telegram...")

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        print("   ✅ TELEGRAM_BOT_TOKEN configurado")
        print(f"   🔑 Token: {token[:10]}...{token[-10:]}")
    else:
        print("   ❌ TELEGRAM_BOT_TOKEN não configurado")

    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if chat_id:
        print(f"   ✅ TELEGRAM_CHAT_ID: {chat_id}")
    else:
        print("   ⚠️ TELEGRAM_CHAT_ID não configurado")

    authorized = os.getenv("TELEGRAM_AUTHORIZED_USERS")
    if authorized:
        users = [u.strip() for u in authorized.split(",")]
        print(f"   ✅ Usuários autorizados: {len(users)} usuários")
    else:
        print("   ⚠️ TELEGRAM_AUTHORIZED_USERS não configurado (permite todos)")


def test_linkedin_config():
    """Testar configurações do LinkedIn"""
    print("🧪 Testando configuração LinkedIn...")

    email = os.getenv("LINKEDIN_EMAIL")
    if email and email != "seu.email@gmail.com":
        print(f"   ✅ Email configurado: {email}")
    else:
        print("   ❌ LINKEDIN_EMAIL não configurado")

    password = os.getenv("LINKEDIN_PASSWORD")
    if password and password != "SuaSenhaSegura123":
        print(f"   ✅ Senha configurada: {'*' * len(password)}")
    else:
        print("   ❌ LINKEDIN_PASSWORD não configurado")


def test_openai_config():
    """Testar configuração OpenAI"""
    print("🧪 Testando configuração OpenAI...")

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith("sk-"):
        print("   ✅ OPENAI_API_KEY configurada")
        print(f"   🔑 Key: {api_key[:10]}...{api_key[-10:]}")

        # Testar conexão
        try:
            import openai

            client = openai.OpenAI(api_key=api_key)

            # Teste simples
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Responda apenas 'OK'"}],
                max_tokens=5,
            )

            print("   ✅ Conexão OpenAI funcionando")

        except Exception as e:
            print(f"   ❌ Erro na conexão OpenAI: {e}")
    else:
        print("   ❌ OPENAI_API_KEY não configurada")


def test_directories():
    """Testar diretórios e permissões"""
    print("🧪 Testando diretórios...")

    # Diretório posts
    posts_dir = Path("posts")
    posts_dir.mkdir(exist_ok=True)

    if posts_dir.exists() and posts_dir.is_dir():
        print(f"   ✅ Diretório posts: {posts_dir.absolute()}")

        # Testar escrita
        test_file = posts_dir / "test_write.txt"
        try:
            test_file.write_text("teste")
            test_file.unlink()
            print("   ✅ Permissão de escrita: OK")
        except Exception as e:
            print(f"   ❌ Erro de escrita: {e}")
    else:
        print("   ❌ Diretório posts não encontrado")

    # Diretório logs
    logs_dir = Path("/logs") if Path("/logs").exists() else Path("logs")
    logs_dir.mkdir(exist_ok=True)

    print(f"   📊 Diretório logs: {logs_dir.absolute()}")


async def run_all_tests():
    """Executar todos os testes"""
    print("🚀 Pipeline Telegram → GPT → LinkedIn - Testes")
    print("=" * 60)

    # Carregar .env
    from dotenv import load_dotenv

    load_dotenv()

    # Executar testes
    test_directories()
    print()

    test_telegram_config()
    print()

    test_openai_config()
    print()

    test_linkedin_config()
    print()

    await test_post_processor()
    print()

    print("✅ Todos os testes concluídos!")
    print()
    print("💡 Próximos passos:")
    print("   1. Configure todas as credenciais no .env")
    print("   2. Execute: ./iniciar_telegram_bot.sh")
    print("   3. Envie /start para seu bot no Telegram")
    print("   4. Envie um arquivo HTML para testar")


if __name__ == "__main__":
    asyncio.run(run_all_tests())

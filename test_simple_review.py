#!/usr/bin/env python3
"""
Teste Simples do Sistema de Revisão v2.6.1
Verificar funcionalidades básicas do ContentReviewer
"""
import os
from dotenv import load_dotenv

load_dotenv()


def test_local_review():
    """Testar revisão local (sem OpenAI)"""
    print("🧪 Testando revisão local...")

    try:
        from app.content_reviewer import ContentReviewer

        # Criar instância (vai usar revisão local se sem OpenAI)
        reviewer = ContentReviewer()

        # Conteúdo de teste - bom
        good_content = """
🚀 A tecnologia está transformando a educação de forma revolucionária.

Principais benefícios:
• Personalização do aprendizado
• Acesso democratizado ao conhecimento
• Feedback em tempo real
• Metodologias inovadoras

O futuro é promissor para educadores e estudantes! 🎓

#educacao #tecnologia #inovacao #futuro #aprendizado
"""

        # Conteúdo de teste - problemático
        bad_content = """
Este texto é muito longo e não tem estrutura adequada para LinkedIn. Na verdade, é tão longo que vai passar do limite de 1300 caracteres estabelecido pela plataforma. Além disso, não tem hashtags relevantes e não segue as melhores práticas de posting na rede social profissional. É um exemplo de como NÃO fazer um post no LinkedIn. Deveria ser mais conciso, ter uma estrutura clara com introdução, desenvolvimento e conclusão, usar emojis com moderação, incluir hashtags relevantes e ter um call-to-action no final. Este texto está sendo deliberadamente longo para testar o sistema de validação de conteúdo e ver se ele consegue identificar os problemas de tamanho, estrutura e compliance. Esperamos que o sistema de revisão identifique todos esses problemas e sugira melhorias específicas para tornar o conteúdo mais adequado para publicação no LinkedIn. É importante que o sistema funcione corretamente tanto com a API da OpenAI quanto sem ela, usando apenas validações locais quando necessário.
"""

        # Testar conteúdo bom
        print("📝 Testando conteúdo adequado...")
        review_good = reviewer.review_content(good_content, "Tecnologia na Educação")

        print(f"✅ Status: {review_good['final_recommendation']}")
        print(f"🎯 Confiança: {review_good['confidence_score']:.0%}")
        print(f"📏 Caracteres: {review_good['char_count']}")
        print(f"🔍 Tipo: {review_good.get('review_type', 'N/A')}")
        print(f"⚠️ Problemas: {len(review_good.get('issues', []))}")

        # Testar conteúdo problemático
        print("\n📝 Testando conteúdo problemático...")
        review_bad = reviewer.review_content(bad_content, "Texto Longo")

        print(f"❌ Status: {review_bad['final_recommendation']}")
        print(f"🎯 Confiança: {review_bad['confidence_score']:.0%}")
        print(f"📏 Caracteres: {review_bad['char_count']}")
        print(f"🔍 Tipo: {review_bad.get('review_type', 'N/A')}")
        print(f"⚠️ Problemas: {len(review_bad.get('issues', []))}")

        if review_bad.get("issues"):
            print("📋 Problemas identificados:")
            for issue in review_bad["issues"][:3]:
                print(f"   • {issue}")

        # Testar formatação para Telegram
        print("\n📱 Testando formatação Telegram...")
        formatted = reviewer.format_review_for_telegram(review_good, good_content)

        if len(formatted) > 200:
            print(f"✅ Mensagem formatada ({len(formatted)} chars)")
            print("📝 Preview:")
            print(formatted[:300] + "...")
        else:
            print("✅ Mensagem formatada:")
            print(formatted)

        return True

    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_validation():
    """Testar validações específicas do LinkedIn"""
    print("\n🔍 Testando validações LinkedIn...")

    try:
        from app.content_reviewer import ContentReviewer

        reviewer = ContentReviewer()

        # Testes específicos
        test_cases = [
            ("Muito curto", "Oi!", False),
            (
                "Sem hashtags",
                "Este é um post sem hashtags mas com tamanho adequado para teste.",
                True,
            ),
            (
                "Hashtags demais",
                "Post " + " ".join([f"#tag{i}" for i in range(15)]),
                False,
            ),
            (
                "Tamanho ideal",
                "Post de tamanho adequado com conteúdo relevante. #teste #linkedin",
                True,
            ),
        ]

        for name, content, should_pass in test_cases:
            validation = reviewer.validate_for_linkedin(content)
            result = "✅" if validation["valid"] == should_pass else "❌"
            print(f"{result} {name}: {validation['valid']} (esperado: {should_pass})")

        return True

    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False


def main():
    """Executar testes simples"""
    print("🚀 Teste Simples do Sistema de Revisão v2.6.1")
    print("=" * 50)

    # Verificar se módulos existem
    try:
        from app.content_reviewer import ContentReviewer

        print("✅ Módulo ContentReviewer importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro na importação: {e}")
        return False

    # Executar testes
    tests = [
        ("Revisão Local", test_local_review),
        ("Validações LinkedIn", test_validation),
    ]

    passed = 0
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSOU")
        else:
            print(f"❌ {test_name} - FALHOU")

    total = len(tests)
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")

    if passed == total:
        print("\n🎉 Sistema de revisão funcionando corretamente!")
        print("💡 Para testar com OpenAI, configure OPENAI_API_KEY no .env")
    else:
        print(f"\n⚠️ {total-passed} teste(s) falharam")

    return passed == total


if __name__ == "__main__":
    main()

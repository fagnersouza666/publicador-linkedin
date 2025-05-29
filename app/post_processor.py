#!/usr/bin/env python3
"""
Post Processor - Processamento inteligente com GPT-4o-mini
Responsável apenas pelo processamento de IA, usando html_parser para extração
"""
import os
import re
import asyncio
from datetime import datetime
from typing import Optional, Dict

from dotenv import load_dotenv
import openai

# Importar nosso parser HTML
from .html_parser import HTMLParser, parse_html_file

# Carregar configurações
load_dotenv()

# Configuração OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")


class PostProcessor:
    """Processador inteligente de conteúdo com GPT-4o-mini"""

    def __init__(self):
        self.model = "gpt-4o-mini"
        self.max_tokens = 2000
        self.temperature = 0.7
        self.html_parser = HTMLParser()

    def create_optimization_prompt(self, content: str, metadata: Dict = None) -> str:
        """Criar prompt otimizado para GPT-4o-mini com contexto"""

        # Contexto adicional baseado nos metadados
        context_info = ""
        if metadata:
            if metadata.get("title"):
                context_info += f"\nTítulo original: {metadata['title']}"
            if metadata.get("description"):
                context_info += f"\nDescrição: {metadata['description'][:200]}"
            if metadata.get("keywords"):
                context_info += (
                    f"\nPalavras-chave: {', '.join(metadata['keywords'][:5])}"
                )

        return f"""
Você é um especialista em marketing de conteúdo e criação de posts profissionais para LinkedIn.

TAREFA: Transforme o texto abaixo em um post LinkedIn envolvente e profissional.
{context_info}

DIRETRIZES:
1. **Tom**: Profissional mas acessível
2. **Tamanho**: Máximo 2300 caracteres (LinkedIn)
3. **Estrutura**: Gancho inicial + desenvolvimento + call-to-action
4. **Hashtags**: 3-5 hashtags relevantes no final
5. **Emojis**: Usar com moderação 
6. **Correção**: Corrigir gramática e ortografia
7. **Fluidez**: Deixar o texto fluído e fácil de ler
8. **Engajamento**: Fazer pergunta ou convite à discussão

TEXTO ORIGINAL:
{content[:3000]}

RESPOSTA: (apenas o post otimizado, sem explicações)
"""

    async def process_with_gpt(self, content: str, metadata: Dict = None) -> str:
        """Processar conteúdo com GPT-4o-mini"""
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em marketing de conteúdo para LinkedIn.",
                    },
                    {
                        "role": "user",
                        "content": self.create_optimization_prompt(content, metadata),
                    },
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            processed_text = response.choices[0].message.content.strip()

            # Validar tamanho (LinkedIn limit atualizado para 1300 chars)
            if len(processed_text) > 1300:
                processed_text = self.truncate_post(processed_text)

            return processed_text

        except openai.OpenAIError as e:
            raise Exception(f"Erro na API OpenAI: {e}")
        except Exception as e:
            raise Exception(f"Erro no processamento GPT: {e}")

    def truncate_post(self, text: str) -> str:
        """Truncar post mantendo integridade"""
        if len(text) <= 1300:
            return text

        # Tentar cortar em ponto, exclamação ou quebra de linha
        for cut_point in [". ", "! ", "\n"]:
            pos = text.rfind(cut_point, 0, 1250)
            if pos > 1000:  # Mínimo razoável
                return text[: pos + 1].strip() + "..."

        # Fallback: corte simples
        return text[:1297] + "..."

    def validate_content(self, content: str) -> Dict[str, any]:
        """Validar conteúdo processado"""
        validation = {"valid": True, "issues": [], "stats": {}}

        # Verificar tamanho
        char_count = len(content)
        validation["stats"]["character_count"] = char_count

        if char_count > 1300:
            validation["valid"] = False
            validation["issues"].append(f"Muito longo: {char_count} chars (máx: 1300)")

        if char_count < 50:
            validation["issues"].append(f"Muito curto: {char_count} chars")

        # Verificar hashtags
        hashtags = re.findall(r"#\w+", content)
        validation["stats"]["hashtag_count"] = len(hashtags)

        if len(hashtags) > 5:
            validation["issues"].append(f"Muitas hashtags: {len(hashtags)} (máx: 5)")

        # Verificar emojis
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map
            "\U0001f1e0-\U0001f1ff"  # flags
            "]+",
            flags=re.UNICODE,
        )
        emojis = emoji_pattern.findall(content)
        validation["stats"]["emoji_count"] = len(emojis)

        if len(emojis) > 5:
            validation["issues"].append(f"Muitos emojis: {len(emojis)} (máx: 5)")

        return validation

    async def process_html_file(self, file_path: str) -> Optional[str]:
        """Processar arquivo HTML completo"""
        try:
            # 1. Extrair texto e metadados usando html_parser
            text, metadata = parse_html_file(file_path)

            if not text or len(text.strip()) < 20:
                raise Exception("Texto extraído muito curto ou vazio")

            # 2. Processar com GPT
            processed_content = await self.process_with_gpt(text, metadata)

            if not processed_content:
                raise Exception("GPT retornou conteúdo vazio")

            # 3. Validar resultado
            validation = self.validate_content(processed_content)

            # 4. Log do processamento
            self.log_processing(
                file_path, text, processed_content, validation, metadata
            )

            return processed_content

        except Exception as e:
            # Log erro
            self.log_error(file_path, str(e))
            raise

    def log_processing(
        self,
        file_path: str,
        original: str,
        processed: str,
        validation: Dict,
        metadata: Dict,
    ) -> None:
        """Log detalhado do processamento"""
        from .linkedin_poster import logger

        logger.info(f"📄 Arquivo processado: {file_path}")
        logger.info(f"📝 Título: {metadata.get('title', 'N/A')}")
        logger.info(f"📏 Tamanho original: {len(original)} chars")
        logger.info(f"📏 Tamanho processado: {len(processed)} chars")
        logger.info(f"📊 Hashtags: {validation['stats'].get('hashtag_count', 0)}")
        logger.info(f"😀 Emojis: {validation['stats'].get('emoji_count', 0)}")
        logger.info(f"📝 Palavras originais: {metadata.get('word_count', 0)}")

        if validation["issues"]:
            logger.warning(f"⚠️ Issues: {', '.join(validation['issues'])}")
        else:
            logger.info("✅ Validação passou")

    def log_error(self, file_path: str, error: str) -> None:
        """Log de erro no processamento"""
        from .linkedin_poster import logger

        logger.error(f"❌ Erro processando {file_path}: {error}")


# Funções de conveniência
async def process_html_to_linkedin(file_path: str) -> str:
    """Função helper para processar HTML para LinkedIn"""
    processor = PostProcessor()
    return await processor.process_html_file(file_path)


# Teste local
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python post_processor.py arquivo.html")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        sys.exit(1)

    async def test():
        try:
            processor = PostProcessor()
            result = await processor.process_html_file(file_path)
            print("✅ Resultado:")
            print("=" * 50)
            print(result)
            print("=" * 50)
            print(f"📏 Tamanho: {len(result)} caracteres")
        except Exception as e:
            print(f"❌ Erro: {e}")

    asyncio.run(test())

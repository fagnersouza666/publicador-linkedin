#!/usr/bin/env python3
"""
Content Reviewer - Revisão de conteúdo pré-publicação
Valida e revisa sem alterar o estilo original
"""
import os
import json
import openai
from typing import Dict, List, Optional
from datetime import datetime

# Configurar OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")


class ContentReviewer:
    """Revisor de conteúdo para validação pré-publicação"""

    def __init__(self):
        # Configurar cliente OpenAI apenas se API key estiver disponível
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None
            print(
                "⚠️ OPENAI_API_KEY não configurado - funcionalidades de revisão IA desabilitadas"
            )

    def review_content(self, content: str, original_title: str = "") -> Dict:
        """
        Revisar conteúdo sem alterar estilo
        Retorna validações e sugestões, não conteúdo alterado
        """

        # Se não tiver OpenAI configurado, fazer apenas validação local
        if not self.client:
            return self._local_review(content, original_title)

        try:
            review_prompt = f"""
MISSÃO: Revisar conteúdo para LinkedIn sem alterar o estilo do autor.

CONTEÚDO PARA REVISÃO:
{content}

TÍTULO ORIGINAL: {original_title}

INSTRUÇÕES DE REVISÃO:
1. NÃO REESCREVER - apenas revisar e apontar problemas
2. Verificar gramática e ortografia
3. Avaliar adequação para LinkedIn profissional
4. Verificar se hashtags são relevantes
5. Avaliar tamanho (ideal 1300 caracteres)
6. Verificar tom profissional
7. Identificar possíveis problemas de compliance

RESPONDER APENAS EM JSON:
{{
  "approved": true/false,
  "issues": ["lista de problemas encontrados"],
  "suggestions": ["sugestões específicas sem reescrever"],
  "compliance_check": {{
    "appropriate_tone": true/false,
    "professional_content": true/false,
    "no_offensive_language": true/false,
    "linkedin_appropriate": true/false
  }},
  "quality_metrics": {{
    "character_count": número,
    "hashtag_count": número,
    "emoji_count": número,
    "readability": "high/medium/low"
  }},
  "final_recommendation": "APPROVE/REVIEW_NEEDED/REJECT",
  "confidence_score": 0.0-1.0
}}
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um revisor de conteúdo LinkedIn. Revise sem alterar o estilo original.",
                    },
                    {"role": "user", "content": review_prompt},
                ],
                max_tokens=800,
                temperature=0.1,
            )

            result = response.choices[0].message.content.strip()

            # Parse JSON response
            review_data = json.loads(result)

            # Adicionar metadata
            review_data["reviewed_at"] = datetime.now().isoformat()
            review_data["original_content"] = content
            review_data["word_count"] = len(content.split())
            review_data["char_count"] = len(content)
            review_data["review_type"] = "ai"

            return review_data

        except json.JSONDecodeError as e:
            return {
                "approved": False,
                "issues": [f"Erro no parsing da revisão: {e}"],
                "final_recommendation": "REVIEW_NEEDED",
                "confidence_score": 0.0,
                "error": "JSON parsing failed",
                "review_type": "error",
            }
        except Exception as e:
            return {
                "approved": False,
                "issues": [f"Erro na revisão: {e}"],
                "final_recommendation": "REVIEW_NEEDED",
                "confidence_score": 0.0,
                "error": str(e),
                "review_type": "error",
            }

    def _local_review(self, content: str, original_title: str = "") -> Dict:
        """Revisão local sem IA quando OpenAI não está disponível"""
        validation = self.validate_for_linkedin(content)

        # Análise básica local
        char_count = len(content)
        hashtag_count = content.count("#")
        emoji_count = sum(1 for char in content if ord(char) > 127)
        word_count = len(content.split())

        # Determinar aprovação baseado em validações locais
        approved = validation["valid"] and len(validation["errors"]) == 0

        issues = validation["errors"] + validation["warnings"]

        suggestions = []
        if char_count > 1300:
            suggestions.append(f"Reduza o conteúdo em {char_count - 1300} caracteres")
        if hashtag_count == 0:
            suggestions.append("Adicione 3-5 hashtags relevantes")
        elif hashtag_count > 10:
            suggestions.append(f"Reduza hashtags de {hashtag_count} para máximo 5")

        recommendation = "APPROVE" if approved else "REVIEW_NEEDED"

        return {
            "approved": approved,
            "issues": issues,
            "suggestions": suggestions,
            "compliance_check": {
                "appropriate_tone": True,  # Não podemos verificar sem IA
                "professional_content": True,
                "no_offensive_language": True,
                "linkedin_appropriate": validation["valid"],
            },
            "quality_metrics": {
                "character_count": char_count,
                "hashtag_count": hashtag_count,
                "emoji_count": emoji_count,
                "readability": "medium",  # Padrão
            },
            "final_recommendation": recommendation,
            "confidence_score": 0.7 if approved else 0.5,  # Confiança menor sem IA
            "reviewed_at": datetime.now().isoformat(),
            "original_content": content,
            "word_count": word_count,
            "char_count": char_count,
            "review_type": "local",  # Indicar que foi revisão local
        }

    def format_review_for_telegram(self, review: Dict, content: str) -> str:
        """Formatar review para exibição no Telegram"""

        # Status principal
        if review["final_recommendation"] == "APPROVE":
            status_emoji = "✅"
            status_text = "APROVADO"
        elif review["final_recommendation"] == "REVIEW_NEEDED":
            status_emoji = "⚠️"
            status_text = "REVISÃO NECESSÁRIA"
        else:
            status_emoji = "❌"
            status_text = "REJEITADO"

        message = f"""
📋 **REVISÃO DE CONTEÚDO**

{status_emoji} **Status:** {status_text}
🎯 **Confiança:** {review.get('confidence_score', 0):.0%}

**📝 CONTEÚDO FINAL:**
{content}

**📊 MÉTRICAS:**
• Caracteres: {review.get('quality_metrics', {}).get('character_count', len(content))}
• Hashtags: {review.get('quality_metrics', {}).get('hashtag_count', 0)}
• Emojis: {review.get('quality_metrics', {}).get('emoji_count', 0)}
"""

        # Adicionar problemas se existirem
        issues = review.get("issues", [])
        if issues:
            message += "\n**⚠️ PROBLEMAS IDENTIFICADOS:**\n"
            for issue in issues[:3]:  # Máximo 3 problemas
                message += f"• {issue}\n"

        # Adicionar sugestões se existirem
        suggestions = review.get("suggestions", [])
        if suggestions:
            message += "\n**💡 SUGESTÕES:**\n"
            for suggestion in suggestions[:2]:  # Máximo 2 sugestões
                message += f"• {suggestion}\n"

        # Compliance check
        compliance = review.get("compliance_check", {})
        compliance_items = []
        if not compliance.get("appropriate_tone", True):
            compliance_items.append("Tom inadequado")
        if not compliance.get("professional_content", True):
            compliance_items.append("Conteúdo não profissional")
        if not compliance.get("linkedin_appropriate", True):
            compliance_items.append("Inadequado para LinkedIn")

        if compliance_items:
            message += f"\n**🚨 COMPLIANCE:** {', '.join(compliance_items)}\n"

        # Instruções
        if review["final_recommendation"] == "APPROVE":
            message += "\n**✅ Aprovar publicação:** /approve"
            message += "\n**❌ Cancelar:** /cancel"
        else:
            message += "\n**📝 Revisar manualmente:** /edit"
            message += "\n**❌ Cancelar:** /cancel"
            message += "\n**🔄 Tentar novamente:** /retry"

        return message

    def validate_for_linkedin(self, content: str) -> Dict:
        """Validações básicas específicas para LinkedIn"""
        validations = {"valid": True, "warnings": [], "errors": []}

        # Tamanho do conteúdo
        if len(content) > 1300:
            validations["errors"].append(
                f"Conteúdo muito longo: {len(content)} chars (máx 1300)"
            )
            validations["valid"] = False
        elif len(content) < 50:
            validations["errors"].append(
                f"Conteúdo muito curto: {len(content)} chars (mín 50)"
            )
            validations["valid"] = False

        # Contagem de hashtags
        hashtag_count = content.count("#")
        if hashtag_count > 10:
            validations["errors"].append(
                f"Muitas hashtags: {hashtag_count} (máximo 10)"
            )
            validations["valid"] = False
        elif hashtag_count > 5:
            validations["warnings"].append(
                f"Muitas hashtags: {hashtag_count} (recomendado 3-5)"
            )
        elif hashtag_count == 0:
            validations["warnings"].append("Sem hashtags (recomendado 3-5)")

        # Contagem de emojis
        emoji_count = sum(
            1 for char in content if ord(char) > 127 and "EMOJI" in str(ord(char))
        )
        if emoji_count > 8:
            validations["warnings"].append(
                f"Muitos emojis: {emoji_count} (máx recomendado 5)"
            )

        # Verificar palavras inadequadas (básico)
        inappropriate_words = ["spam", "click here", "buy now", "urgent"]
        found_words = [
            word for word in inappropriate_words if word.lower() in content.lower()
        ]
        if found_words:
            validations["warnings"].append(
                f"Palavras não recomendadas: {', '.join(found_words)}"
            )

        return validations

    def save_review(self, review: Dict, file_path: str) -> str:
        """Salvar review junto com o arquivo"""
        review_path = file_path.replace(".html", ".review.json")

        try:
            with open(review_path, "w", encoding="utf-8") as f:
                json.dump(review, f, indent=2, ensure_ascii=False)
            return review_path
        except Exception as e:
            print(f"Erro ao salvar review: {e}")
            return ""

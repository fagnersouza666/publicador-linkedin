#!/usr/bin/env python3
"""
HTML Parser - Extração e processamento de conteúdo HTML
Responsável apenas pela extração e limpeza de texto de arquivos HTML
"""
import os
import re
import json
from datetime import datetime
from typing import Optional, Dict, Tuple
from pathlib import Path

from bs4 import BeautifulSoup, Comment


class HTMLParser:
    """Parser inteligente de conteúdo HTML"""

    def __init__(self):
        self.supported_tags = [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",  # Títulos
            "p",
            "div",
            "article",
            "section",  # Parágrafos
            "li",
            "ul",
            "ol",  # Listas
            "blockquote",
            "em",
            "strong",
            "b",  # Formatação
        ]

        self.exclude_tags = [
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form",
            "button",
        ]

        self.content_selectors = [
            "main",
            "article",
            ".content",
            ".post",
            ".article",
            "#content",
            "#main",
        ]

    def extract_metadata(self, file_path: str) -> Dict:
        """Extrair metadados do arquivo HTML"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")

            metadata = {
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "extracted_at": datetime.now().isoformat(),
                "title": "",
                "description": "",
                "author": "",
                "keywords": [],
                "word_count": 0,
                "char_count": 0,
                "images": [],
                "links": [],
            }

            # Título
            title_tag = soup.find("title")
            if title_tag:
                metadata["title"] = title_tag.get_text().strip()

            # Meta description
            desc_tag = soup.find("meta", attrs={"name": "description"})
            if desc_tag:
                metadata["description"] = desc_tag.get("content", "").strip()

            # Meta author
            author_tag = soup.find("meta", attrs={"name": "author"})
            if author_tag:
                metadata["author"] = author_tag.get("content", "").strip()

            # Meta keywords
            keywords_tag = soup.find("meta", attrs={"name": "keywords"})
            if keywords_tag:
                keywords = keywords_tag.get("content", "").strip()
                metadata["keywords"] = [k.strip() for k in keywords.split(",")]

            # H1 como título alternativo
            if not metadata["title"]:
                h1_tag = soup.find("h1")
                if h1_tag:
                    metadata["title"] = h1_tag.get_text().strip()

            # Contagem básica de texto
            text = self.extract_text_from_html(file_path)
            metadata["char_count"] = len(text)
            metadata["word_count"] = len(text.split())

            # Imagens
            for img in soup.find_all("img"):
                img_data = {
                    "src": img.get("src", ""),
                    "alt": img.get("alt", ""),
                    "title": img.get("title", ""),
                }
                metadata["images"].append(img_data)

            # Links
            for link in soup.find_all("a", href=True):
                link_data = {
                    "href": link.get("href"),
                    "text": link.get_text().strip()[:100],  # Limitar texto
                    "title": link.get("title", ""),
                }
                metadata["links"].append(link_data)

            return metadata

        except Exception as e:
            raise Exception(f"Erro ao extrair metadados: {e}")

    def extract_text_from_html(self, file_path: str) -> str:
        """Extrair texto limpo de arquivo HTML"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Parse com BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")

            # Remover elementos indesejados
            for element in soup(self.exclude_tags):
                element.decompose()

            # Remover comentários
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()

            # Extrair texto principal - priorizar content areas
            main_content = self._find_main_content(soup)

            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()

            # Limpar texto
            text = self._clean_text(text)

            return text

        except Exception as e:
            raise Exception(f"Erro ao extrair texto do HTML: {e}")

    def _find_main_content(self, soup: BeautifulSoup) -> Optional:
        """Encontrar a área principal de conteúdo"""
        # Tentar seletores específicos de conteúdo
        for selector in self.content_selectors:
            if selector.startswith(".") or selector.startswith("#"):
                content = soup.select_one(selector)
            else:
                content = soup.find(selector)

            if content and content.get_text().strip():
                return content

        # Fallback: procurar por maior bloco de texto
        candidates = soup.find_all(
            ["main", "article", "div"], class_=re.compile(r"content|post|article", re.I)
        )

        if candidates:
            # Retornar o candidato com mais texto
            return max(candidates, key=lambda x: len(x.get_text()))

        return soup.find("body")

    def _clean_text(self, text: str) -> str:
        """Limpar e normalizar texto extraído"""
        # Normalizar espaços em branco
        text = re.sub(r"\s+", " ", text)

        # Normalizar quebras de linha
        text = re.sub(r"\n+", "\n", text)

        # Remover linhas muito curtas (provavelmente nav/footer)
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Manter linhas com conteúdo substancial
            if len(line) > 20 or any(
                line.lower().startswith(prefix)
                for prefix in ["•", "-", "1.", "2.", "3."]
            ):
                cleaned_lines.append(line)

        text = "\n".join(cleaned_lines).strip()

        # Remover múltiplas quebras consecutivas
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text

    def create_slug(self, title: str, max_length: int = 50) -> str:
        """Criar slug para nome de arquivo"""
        if not title:
            return "sem_titulo"

        # Converter para minúsculas e remover acentos básicos
        slug = title.lower()

        # Mapa de acentos comuns
        accent_map = {
            "á": "a",
            "à": "a",
            "ã": "a",
            "â": "a",
            "ä": "a",
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "í": "i",
            "ì": "i",
            "î": "i",
            "ï": "i",
            "ó": "o",
            "ò": "o",
            "õ": "o",
            "ô": "o",
            "ö": "o",
            "ú": "u",
            "ù": "u",
            "û": "u",
            "ü": "u",
            "ç": "c",
            "ñ": "n",
        }

        for accented, normal in accent_map.items():
            slug = slug.replace(accented, normal)

        # Manter apenas letras, números e alguns caracteres
        slug = re.sub(r"[^a-z0-9\s\-_]", "", slug)

        # Substituir espaços por hífens
        slug = re.sub(r"\s+", "-", slug)

        # Remover hífens múltiplos
        slug = re.sub(r"-+", "-", slug)

        # Remover hífens do início e fim
        slug = slug.strip("-")

        # Limitar tamanho
        if len(slug) > max_length:
            slug = slug[:max_length].rsplit("-", 1)[0]

        return slug or "sem_titulo"

    def validate_html_content(self, file_path: str) -> Dict:
        """Validar se o arquivo HTML tem conteúdo válido"""
        validation = {"valid": True, "issues": [], "warnings": [], "stats": {}}

        try:
            # Verificar se arquivo existe
            if not os.path.exists(file_path):
                validation["valid"] = False
                validation["issues"].append("Arquivo não encontrado")
                return validation

            # Verificar tamanho do arquivo
            file_size = os.path.getsize(file_path)
            validation["stats"]["file_size_bytes"] = file_size

            if file_size == 0:
                validation["valid"] = False
                validation["issues"].append("Arquivo vazio")
                return validation

            if file_size > 10 * 1024 * 1024:  # 10MB
                validation["valid"] = False
                validation["issues"].append(
                    f"Arquivo muito grande: {file_size/1024/1024:.1f}MB"
                )
                return validation

            # Extrair texto e metadados
            text = self.extract_text_from_html(file_path)
            metadata = self.extract_metadata(file_path)

            validation["stats"].update(
                {
                    "char_count": len(text),
                    "word_count": len(text.split()),
                    "title": metadata.get("title", ""),
                    "has_title": bool(metadata.get("title")),
                    "images_count": len(metadata.get("images", [])),
                    "links_count": len(metadata.get("links", [])),
                }
            )

            # Validações de conteúdo
            if len(text.strip()) < 50:
                validation["valid"] = False
                validation["issues"].append(
                    f"Conteúdo muito curto: {len(text)} caracteres"
                )

            if len(text.split()) < 10:
                validation["warnings"].append(f"Poucas palavras: {len(text.split())}")

            if not metadata.get("title"):
                validation["warnings"].append("Título não encontrado")

            # Verificar se é HTML válido
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "<html" not in content.lower() and "<body" not in content.lower():
                validation["warnings"].append("Estrutura HTML básica não detectada")

        except Exception as e:
            validation["valid"] = False
            validation["issues"].append(f"Erro na validação: {e}")

        return validation


# Funções de conveniência
def parse_html_file(file_path: str) -> Tuple[str, Dict]:
    """Função helper para extrair texto e metadados"""
    parser = HTMLParser()
    text = parser.extract_text_from_html(file_path)
    metadata = parser.extract_metadata(file_path)
    return text, metadata


def validate_html_file(file_path: str) -> Dict:
    """Função helper para validar arquivo HTML"""
    parser = HTMLParser()
    return parser.validate_html_content(file_path)


def create_filename_slug(title: str) -> str:
    """Função helper para criar slug de arquivo"""
    parser = HTMLParser()
    return parser.create_slug(title)


# Teste local
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python html_parser.py arquivo.html")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        sys.exit(1)

    try:
        parser = HTMLParser()

        print("🔍 Validando arquivo...")
        validation = parser.validate_html_content(file_path)

        if not validation["valid"]:
            print("❌ Arquivo inválido:")
            for issue in validation["issues"]:
                print(f"   - {issue}")
            sys.exit(1)

        print("✅ Arquivo válido!")

        if validation["warnings"]:
            print("⚠️ Avisos:")
            for warning in validation["warnings"]:
                print(f"   - {warning}")

        print(f"📊 Estatísticas: {validation['stats']}")

        print("\n📄 Extraindo texto...")
        text = parser.extract_text_from_html(file_path)

        print(f"✅ Texto extraído: {len(text)} caracteres")
        print("=" * 50)
        print(text[:500] + "..." if len(text) > 500 else text)
        print("=" * 50)

        print("\n📋 Extraindo metadados...")
        metadata = parser.extract_metadata(file_path)

        print(f"📝 Título: {metadata.get('title', 'N/A')}")
        print(f"📝 Descrição: {metadata.get('description', 'N/A')[:100]}...")
        print(f"📊 Palavras: {metadata.get('word_count', 0)}")
        print(f"🖼️ Imagens: {len(metadata.get('images', []))}")
        print(f"🔗 Links: {len(metadata.get('links', []))}")

        # Teste de slug
        title = metadata.get("title", "teste")
        slug = parser.create_slug(title)
        print(f"🔗 Slug: {slug}")

    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

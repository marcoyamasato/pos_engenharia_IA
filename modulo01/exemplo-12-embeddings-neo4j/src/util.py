"""Equivalente ao util.ts: imprime os resultados da busca."""
import re

from langchain_core.documents import Document


def format_content(content: str, max_length: int = 200) -> str:
    cleaned = re.sub(r"\s+", " ", content).strip()
    return f"{cleaned[:max_length]}..." if len(cleaned) > max_length else cleaned


def display_results(results: list[Document]) -> None:
    print(f"\n📄 Encontrados {len(results)} trechos relevantes:\n")
    for i, doc in enumerate(results, start=1):
        print(f"   {i}.")
        print(f"      {format_content(doc.page_content)}")
        if page := doc.metadata.get("page"):
            print(f"      📄 (Página: {page})")
        print()

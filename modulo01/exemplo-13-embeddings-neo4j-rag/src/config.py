"""Equivalente ao config.ts: todas as configurações num só lugar."""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # lê o .env (não o .env.example!)

PROMPTS_FOLDER = Path("./prompts")


def _read_text(path: Path) -> str:
    # encoding="utf-8" é obrigatório no Windows: lá o padrão é cp1252 e os acentos quebram
    return path.read_text(encoding="utf-8")


@dataclass(frozen=True)
class Neo4jConfig:
    url: str = os.environ["NEO4J_URI"]
    username: str = os.environ["NEO4J_USER"]
    password: str = os.environ["NEO4J_PASSWORD"]
    index_name: str = "tensors_index"
    node_label: str = "Chunk"
    text_node_properties: tuple[str, ...] = ("text",)
    embedding_node_property: str = "embedding"


@dataclass(frozen=True)
class OpenRouterConfig:
    nlp_model: str = os.environ["NLP_MODEL"]
    url: str = "https://openrouter.ai/api/v1"
    api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    temperature: float = 0.3
    max_retries: int = 2
    # Cabeçalhos opcionais que o OpenRouter usa para identificar o seu app
    default_headers: dict = field(default_factory=lambda: {
        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", ""),
        "X-Title": os.getenv("OPENROUTER_SITE_NAME", ""),
    })


@dataclass(frozen=True)
class TextSplitterConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass(frozen=True)
class Config:
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    open_router: OpenRouterConfig = field(default_factory=OpenRouterConfig)
    text_splitter: TextSplitterConfig = field(default_factory=TextSplitterConfig)
    pdf_path: str = "./tensores.pdf"
    embedding_model: str = os.environ["EMBEDDING_MODEL"]
    top_k: int = 3
    score_threshold: float = float(os.getenv("NEO4J_VECTOR_THRESHOLD", "0.5"))
    # NOVO no exemplo 13: o prompt fica fora do código, em arquivos
    prompt_config: dict = field(
        default_factory=lambda: json.loads(_read_text(PROMPTS_FOLDER / "answerPrompt.json"))
    )
    template_text: str = field(default_factory=lambda: _read_text(PROMPTS_FOLDER / "template.txt"))
    answers_folder: Path = Path("./respostas")
    answers_file_name: str = "resposta"


CONFIG = Config()

# Fail fast: melhor um erro claro agora do que um "401 Unauthorized" confuso lá na frente
if not CONFIG.open_router.api_key:
    raise SystemExit("❌ Preencha OPENROUTER_API_KEY no arquivo .env (crie em https://openrouter.ai/keys)")

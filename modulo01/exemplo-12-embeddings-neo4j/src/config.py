"""Equivalente ao config.ts: todas as configurações num só lugar."""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()  # equivalente ao `node --env-file .env`


# frozen=True -> imutável, igual ao Object.freeze() do JS
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
class TextSplitterConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass(frozen=True)
class Config:
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    text_splitter: TextSplitterConfig = field(default_factory=TextSplitterConfig)
    pdf_path: str = "./tensores.pdf"
    embedding_model: str = os.environ["EMBEDDING_MODEL"]
    top_k: int = 3


CONFIG = Config()

"""Equivalente ao documentProcessor.ts: lê o PDF e corta em chunks."""
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import TextSplitterConfig


class DocumentProcessor:
    def __init__(self, pdf_path: str, splitter_config: TextSplitterConfig):
        self.pdf_path = pdf_path
        self.splitter_config = splitter_config

    def load_and_split(self) -> list[Document]:
        raw_documents = PyPDFLoader(self.pdf_path).load()  # 1 Document por página
        print(f"📄 Loaded {len(raw_documents)} pages from PDF")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.splitter_config.chunk_size,
            chunk_overlap=self.splitter_config.chunk_overlap,
        )
        documents = splitter.split_documents(raw_documents)
        print(f"✂️  Split into {len(documents)} chunks")

        # Mantém só o metadado 'source' (igual ao .map() do JS)
        return [
            Document(page_content=d.page_content, metadata={"source": d.metadata["source"]})
            for d in documents
        ]

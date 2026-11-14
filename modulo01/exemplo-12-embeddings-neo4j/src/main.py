"""Equivalente ao index.ts: popula o Neo4j e faz buscas por similaridade."""
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jVector

from config import CONFIG
from document_processor import DocumentProcessor
from util import display_results

QUESTIONS = [
    "O que são tensores e como são representados em JavaScript?",
    "Como converter objetos JavaScript em tensores?",
    "O que é normalização de dados e por que é necessária?",
    "Como funciona uma rede neural no TensorFlow.js?",
    "O que significa treinar uma rede neural?",
    "o que é hot enconding e quando usar?",
]


def clear_all(store: Neo4jVector, node_label: str) -> None:
    print("🗑️  Removendo todos os documentos existentes...")
    store.query(f"MATCH (n:`{node_label}`) DETACH DELETE n")
    print("✅ Documentos removidos com sucesso\n")


def main() -> None:
    print("🚀 Inicializando sistema de Embeddings com Neo4j...\n")

    # ETAPA 1: PDF -> chunks -> embeddings -> Neo4j
    documents = DocumentProcessor(CONFIG.pdf_path, CONFIG.text_splitter).load_and_split()

    embeddings = HuggingFaceEmbeddings(model_name=CONFIG.embedding_model)
    # vetor = embeddings.embed_query("JavaScript")  # descomente para ver o vetor
    # print(len(vetor), vetor[:5])

    neo = CONFIG.neo4j
    store = Neo4jVector.from_existing_graph(
        embedding=embeddings,
        url=neo.url,
        username=neo.username,
        password=neo.password,
        index_name=neo.index_name,
        node_label=neo.node_label,
        text_node_properties=list(neo.text_node_properties),
        embedding_node_property=neo.embedding_node_property,
    )
    try:
        clear_all(store, neo.node_label)  # síncrono: termina antes de inserir
        for i, doc in enumerate(documents, start=1):
            print(f"✅ Adicionando documento {i}/{len(documents)}")
            store.add_documents([doc])
        print("\n✅ Base de dados populada com sucesso!\n")

        # ETAPA 2: busca por similaridade
        print("🔍 ETAPA 2: Executando buscas por similaridade...\n")
        for question in QUESTIONS:
            print(f"\n{'=' * 80}\n📌 PERGUNTA: {question}\n{'=' * 80}")
            display_results(store.similarity_search(question, k=CONFIG.top_k))

        print(f"\n{'=' * 80}\n✅ Processamento concluído com sucesso!\n")
    finally:
        store._driver.close()  # equivalente ao vectorStore.close()


if __name__ == "__main__":
    main()

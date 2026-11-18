"""Equivalente ao index.ts: indexa o PDF e responde perguntas com RAG."""
import time

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jVector
from langchain_openai import ChatOpenAI

from ai import AI
from config import CONFIG
from document_processor import DocumentProcessor

QUESTIONS = [
    # "O que são tensores e como são representados em JavaScript?",  (comentada na aula)
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

    # ===== ETAPA 1: indexação (igual ao exemplo 12) =====
    documents = DocumentProcessor(CONFIG.pdf_path, CONFIG.text_splitter).load_and_split()
    embeddings = HuggingFaceEmbeddings(model_name=CONFIG.embedding_model)

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

    # ===== NOVO: o LLM, via OpenRouter =====
    # ChatOpenAI fala o "idioma" da API da OpenAI; o OpenRouter entende esse idioma.
    # Trocando base_url + api_key, usamos qualquer modelo do OpenRouter (aqui, Gemma do Google).
    router = CONFIG.open_router
    nlp_model = ChatOpenAI(
        model=router.nlp_model,
        api_key=router.api_key,
        base_url=router.url,
        temperature=router.temperature,
        max_retries=router.max_retries,
        default_headers=router.default_headers,
    )

    try:
        clear_all(store, neo.node_label)
        for i, doc in enumerate(documents, start=1):
            print(f"✅ Adicionando documento {i}/{len(documents)}")
            store.add_documents([doc])
        print("\n✅ Base de dados populada com sucesso!\n")

        # ===== ETAPA 2: perguntas respondidas com RAG =====
        print("🔍 ETAPA 2: Respondendo perguntas com RAG...\n")
        ai = AI(
            nlp_model=nlp_model,
            vector_store=store,
            prompt_config=CONFIG.prompt_config,
            template_text=CONFIG.template_text,
            top_k=CONFIG.top_k,
            score_threshold=CONFIG.score_threshold,
        )
        CONFIG.answers_folder.mkdir(parents=True, exist_ok=True)  # mkdir -p

        for index, question in enumerate(QUESTIONS):
            print(f"\n{'=' * 80}\n📌 PERGUNTA: {question}\n{'=' * 80}")
            result = ai.answer_question(question)
            if "error" in result:
                print(f"\n❌ Erro: {result['error']}\n")
                continue

            # time.time_ns() // 1_000_000 = milissegundos, igual ao Date.now() do JS
            file = CONFIG.answers_folder / f"{CONFIG.answers_file_name}-{index}-{time.time_ns() // 1_000_000}.md"
            file.write_text(result["answer"], encoding="utf-8")
            print(f"💾 Salvo em {file}")

        print(f"\n{'=' * 80}\n✅ Processamento concluído com sucesso!\n")
    finally:
        store._driver.close()


if __name__ == "__main__":
    main()

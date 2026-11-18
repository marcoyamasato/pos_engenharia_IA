"""Equivalente ao ai.ts: o pipeline RAG.

    pergunta -> [R] busca no Neo4j -> [A] monta o prompt -> [G] LLM gera a resposta
"""
from typing import Callable, NotRequired, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.vectorstores import VectorStore

NOT_FOUND = "Desculpe, não encontrei informações relevantes sobre essa pergunta na base de conhecimento."


class ChainState(TypedDict):
    """O 'formulário' que passa de etapa em etapa (interface ChainState do TS)."""
    question: str
    context: NotRequired[str]
    top_score: NotRequired[float]
    error: NotRequired[str]
    answer: NotRequired[str]


class AI:
    def __init__(
        self,
        nlp_model: BaseChatModel,
        vector_store: VectorStore,
        prompt_config: dict,
        template_text: str,
        top_k: int,
        score_threshold: float,
        debug_log: Callable[..., None] = print,
    ):
        self.nlp_model = nlp_model
        self.vector_store = vector_store
        self.prompt_config = prompt_config
        self.template_text = template_text
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.debug_log = debug_log

    # ---------- Etapa 1: [R]etrieval ----------
    def retrieve_vector_search_results(self, state: ChainState) -> ChainState:
        self.debug_log("🔍 Buscando no vector store do Neo4j...")
        # Diferente do exemplo 12: devolve pares (Document, score)
        results = self.vector_store.similarity_search_with_score(state["question"], k=self.top_k)

        if not results:
            self.debug_log("⚠️  Nenhum resultado encontrado no vector store.")
            return {**state, "error": NOT_FOUND}

        top_score = results[0][1]
        self.debug_log(f"✅ Encontrados {len(results)} resultados (melhor score: {top_score:.3f})")

        relevant = [doc.page_content for doc, score in results if score > self.score_threshold]

        # DIFERENÇA DA AULA: lá, se o filtro descartasse tudo, o LLM era chamado
        # com contexto vazio. Aqui paramos antes e não gastamos uma chamada de API.
        if not relevant:
            self.debug_log(f"⚠️  Nenhum trecho passou do score mínimo ({self.score_threshold}).")
            return {**state, "top_score": top_score, "error": NOT_FOUND}

        # {**state, ...} = copia o dict e sobrescreve campos (o "...input" do JS)
        return {**state, "context": "\n\n---\n\n".join(relevant), "top_score": top_score}

    # ---------- Etapa 2: [A]ugmented + [G]eneration ----------
    def generate_nlp_response(self, state: ChainState) -> ChainState:
        if "error" in state:  # etapa anterior falhou: não chama o LLM
            return state
        self.debug_log("🤖 Gerando resposta com IA...")

        prompt = ChatPromptTemplate.from_template(self.template_text)
        # LCEL: o "|" encadeia etapas (no JS: .pipe())
        chain = prompt | self.nlp_model | StrOutputParser()

        cfg = self.prompt_config
        answer = chain.invoke({
            "role": cfg["role"],
            "task": cfg["task"],
            "tone": cfg["constraints"]["tone"],
            "language": cfg["constraints"]["language"],
            "format": cfg["constraints"]["format"],
            "instructions": "\n".join(f"{i}. {txt}" for i, txt in enumerate(cfg["instructions"], start=1)),
            "question": state["question"],
            "context": state["context"],
        })
        return {**state, "answer": answer}

    # ---------- Junta as duas etapas ----------
    def answer_question(self, question: str) -> ChainState:
        # RunnableSequence.from([...]) do JS. Sem .bind(this): em Python o self já vem junto
        chain = RunnableLambda(self.retrieve_vector_search_results) | RunnableLambda(self.generate_nlp_response)
        result = chain.invoke({"question": question})

        self.debug_log("\n🎙️  Pergunta:")
        self.debug_log(question, "\n")
        self.debug_log("💬 Resposta:")
        self.debug_log(result.get("answer") or result.get("error"), "\n")
        return result

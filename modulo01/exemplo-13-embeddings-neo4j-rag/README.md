# Exemplo 13 — RAG: Embeddings + Neo4j + LLM (versão Python)

Original (JS): `modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-13-embeddings-neo4j-rag`

O que muda em relação ao exemplo 12: depois da busca por similaridade, os trechos
encontrados vão para um LLM (via OpenRouter), que escreve a resposta. As respostas
são salvas em `respostas/`.

| Arquivo | Papel |
|---|---|
| `src/ai.py` | **Novo.** Pipeline RAG: busca (R) → prompt (A) → LLM (G) |
| `prompts/answerPrompt.json` | **Novo.** Papel, tom e instruções do assistente |
| `prompts/template.txt` | **Novo.** Texto do prompt com lacunas `{...}` |
| `src/config.py` | + OpenRouter, prompts, threshold |
| `src/main.py` | + cria o LLM e responde as perguntas |
| `src/document_processor.py`, `docker-compose.yml` | Iguais ao exemplo 12 |

## Diferenças em relação à aula (de propósito)
1. `NEO4J_VECTOR_THRESHOLD` do `.env` é lido de verdade (na aula estava fixo em 0.5 no código).
2. Se nenhum trecho passa do threshold, o LLM não é chamado (na aula ia com contexto vazio).
3. `prompts/template.txt` começa com `{role}.` em vez de `Você é um {role}.`: o `role` do JSON já começa com "Você é um", e na aula o prompt saía "Você é um Você é um assistente...".
4. Falta da `OPENROUTER_API_KEY` gera erro claro logo no início.
5. `util.py` não existe aqui: no exemplo 13 da aula o `displayResults` deixou de ser usado.

## Rodando (Windows / PowerShell, com pip)
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    copy .env.example .env        # e preencha OPENROUTER_API_KEY
    docker compose up -d --wait
    python src/main.py

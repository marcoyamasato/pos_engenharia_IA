# Exemplo 12 — Embeddings + Neo4j (versão Python)

Original (JS): `modulo01-fundamentos-de-ia-e-llms-para-programadores/exemplo-12-embeddings-neo4j`

| JS (aula)          | Python (aqui)       |
|--------------------|---------------------|
| `npm ci`           | `uv sync`           |
| `npm run infra:up` | `docker compose up -d --wait` |
| `npm start`        | `uv run python src/main.py` |
| `npm run infra:down` | `docker compose down --volumes` |

## Rodando
    cp .env.example .env
    uv sync
    docker compose up -d --wait
    uv run python src/main.py

Neo4j Browser: http://localhost:7474 (neo4j / password)

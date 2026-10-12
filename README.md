# vocab-generator

Simple Docker project for a local-network Norwegian vocabulary service.

## Phase 0 status

- FastAPI service skeleton
- SQLite readiness check
- `GET /health` endpoint
- Docker healthcheck
- CI workflow for tests and image build

## Phase 1 status

- Bundled static dataset at `data/vocabulary.json`
- Baseline pre-used seed list at `data/seed/top500_common_norwegian.txt`
- `GET /word` endpoint with active-word persistence in SQLite
- Deterministic error contracts (`DB_UNAVAILABLE`, `DATASET_UNAVAILABLE`)

Seed list provenance: `data/seed/top500_common_norwegian.txt` is normalized from
https://www.korrekturavdelingen.no/ord-uttrykk-frekvensordliste-500-vanligste-norsk.htm.

## Run locally (without Docker)

```bash
uv sync --dev
uv run uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Health check:

```bash
curl http://localhost:8080/health
```

## Run with Docker Compose

```bash
docker compose up -d --build
curl http://localhost:8080/health
```

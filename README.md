# vocab-generator

Local-network Docker service that generates random Norwegian vocabulary entries
with English equivalents and bilingual definitions.

## Overview

- Designed for self-hosted LAN use and integration with other local services.
- Persists active/used-word state in SQLite to avoid duplicates within a cycle.
- Applies a baseline pre-used common-word seed list before normal generation.
- Exposes a simple REST API for fetch, refresh, health, and metrics.

## Functionality

- `GET /word`
  - returns the current active vocabulary entry.
  - if no active entry exists, selects and persists one from the static dataset.
- `POST /word/new`
  - marks the previous active word as used and returns a new unique entry.
- `GET /health`
  - returns service readiness (`ok`/`degraded`) based on API + DB state.
- `GET /metrics`
  - returns in-memory request/error/cycle telemetry.

- Deterministic error contracts:
  - `DB_UNAVAILABLE`
  - `DATASET_UNAVAILABLE`

## Data Sources

- Static vocabulary dataset: `data/vocabulary.json`
- Dataset provenance metadata: `data/vocabulary-source.json`
- Baseline seed list: `data/seed/top500_common_norwegian.txt`
- Seed list provenance: https://www.korrekturavdelingen.no/ord-uttrykk-frekvensordliste-500-vanligste-norsk.htm
- Vocabulary corpus source: Kaikki/Wiktextract Norwegian Bokmal export

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

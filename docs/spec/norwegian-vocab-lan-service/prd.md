# Norwegian Vocabulary LAN Service

## One-liner

Build a local-network Dockerized API service that returns random Norwegian words with English equivalents and bilingual definitions, persists generated words to avoid duplicates, and supports forced generation of a new word on demand.

## Status

- Stage: Draft
- PRD slug: norwegian-vocab-lan-service
- Owners: TBD
- Reviewers: TBD

## Context

### Problem

Today there is no standardized local service that other LAN services can query for bilingual Norwegian-English vocabulary. Word generation and deduplication are ad hoc, and there is no persisted anti-duplicate state across container restarts.

### Goals

- Provide a simple REST API for LAN consumers to fetch a word payload and request a new word.
- Guarantee no duplicates within a dataset cycle by persisting generated-word state.
- Keep the service self-contained and reliable offline via a bundled static dataset.
- Integrate with `glance-app` so the dashboard can display the current word and trigger a refresh action.
- Start generation beyond a pre-used baseline of the 500 most common Norwegian words.

### Non-Goals / Out of Scope

- Public internet exposure, internet-facing auth, or multi-tenant identity.
- Rich dictionary features (etymology, pronunciation audio, parts-of-speech ranking).
- Admin UI or browser UI.
- Horizontal multi-node synchronization.
- Building or forking a custom `glance-app` widget engine.

### Users and Use Cases

- Primary user(s): Internal LAN services and scripts that need random Norwegian vocabulary data.
- Key use case(s):
    1. A local service calls `GET /word` to retrieve the current active bilingual vocabulary entry.
    2. A user-triggered action calls `POST /word/new` to force replacement with the next unique entry.

### Assumptions

- Service runs in a trusted local network where no-auth access is acceptable.
- Each vocabulary entry includes one primary Norwegian definition and one primary English definition.
- Dataset can be loaded fully in memory at startup.
- The 500 most common Norwegian words from `korrekturavdelingen.no` are represented in a seed list and treated as already used at initialization.

### Constraints

- Technical: Python + FastAPI, REST/JSON interface, Docker deployment, SQLite on mounted volume.
- Legal/Privacy/Security: No user PII is stored; dataset licensing must be validated before release.
- Operational: Service must be reachable from peer LAN hosts and support health checks for orchestration.

### Dependencies / External Systems

- Upstream systems: none at runtime (offline static dataset).
- Downstream systems: LAN consumers and `glance-app` dashboard consuming word display and refresh flows.
- Third-party vendors: none at runtime.
- Data stores/queues: SQLite database file persisted via Docker volume.

### DO NOT CHANGE

- Protocol remains REST/JSON for this release.
- LAN trust model remains no-auth and must not be expanded to internet exposure in this scope.
- Duplicate policy remains global uniqueness per cycle with explicit cycle reset on exhaustion.

## Proposed Solution (High Level)

Implement a FastAPI service in Docker that binds to `0.0.0.0` and exposes a small REST contract:

- `GET /word`: Returns the active word payload. If none exists, it selects a random unused word from the current cycle, persists it, and returns it.
- `POST /word/new`: Forces generation of a replacement word, marks the previous active word as used, persists the new active word, and returns it.
- `GET /health`: Returns service and DB readiness.

The service loads a bundled static dataset containing Norwegian and English terms plus definitions in both languages. Used words are tracked in SQLite so duplicate prevention survives container restarts. When all words in the dataset are used, the service increments `cycle_id`, resets uniqueness tracking for the new cycle, and continues generation while emitting a reset log.

Related diagrams (reference by relative path):

- [user flow: fetch and refresh](diagrams/01-user-flow-word-fetch-and-refresh.md)
- [API sequence: generate and persist](diagrams/02-api-sequence-generate-and-persist-word.md)
- [domain state: cycle lifecycle](diagrams/03-domain-state-word-cycle-lifecycle.md)

## Requirements

### Functional Requirements

FR-1: The service must expose `GET /word` that returns JSON with `word_id`, `norwegian_word`, `english_word`, `norwegian_definition`, `english_definition`, `cycle_id`, and `generated_at`.

- Acceptance Criteria:
    - When no active word exists, and `GET /word` is called, then the response is HTTP 200 with all required fields populated.
    - When an active word exists, and `GET /word` is called, then the same active word is returned until `POST /word/new` is called.
- Verification:
    - Integration test: `pytest -q tests/integration/test_get_word.py`.

FR-2: The service must expose `POST /word/new` that forces generation of a new active word and marks the previous active word as used.

- Acceptance Criteria:
    - When `POST /word/new` is called after a prior active word exists, then response is HTTP 200 and `word_id` differs from the previous active word.
    - After `POST /word/new`, a subsequent `GET /word` returns the new active word.
- Verification:
    - Integration test: `pytest -q tests/integration/test_new_word.py`.

FR-3: The service must prevent duplicates globally within a cycle by persisting used-word state in SQLite.

- Acceptance Criteria:
    - On first initialization, the service seeds used-word state with a baseline list containing the 500 most common Norwegian words so they are treated as already used.
    - Across sequential `POST /word/new` calls within a cycle, no `word_id` repeats until all dataset entries have been used.
    - When the cycle is exhausted, the next generation increments `cycle_id` and resumes selection from the full dataset.
- Verification:
    - Integration test with finite fixture dataset: `pytest -q tests/integration/test_uniqueness_cycle.py`.
    - Seed test: `pytest -q tests/integration/test_seed_used_words.py` verifies baseline IDs are marked used on first startup.
    - DB state assertion in test verifies persisted used-word records and cycle transition.

FR-4: The service must provide `GET /health` that reports readiness based on API process health and SQLite connectivity.

- Acceptance Criteria:
    - When API and DB are available, `GET /health` returns HTTP 200 and status `ok`.
    - When DB connectivity fails, `GET /health` returns HTTP 503 and status `degraded`.
- Verification:
    - Integration test: `pytest -q tests/integration/test_health.py`.
    - Docker healthcheck command returns success in healthy state.

FR-5: The service must return deterministic error responses for operational failures.

- Acceptance Criteria:
    - DB unavailability returns HTTP 503 with machine-readable `error_code` = `DB_UNAVAILABLE`.
    - Dataset load failure returns HTTP 500 with machine-readable `error_code` = `DATASET_UNAVAILABLE`.
- Verification:
    - Integration test: `pytest -q tests/integration/test_error_contracts.py`.

FR-6: The service must support `glance-app` integration for both word display and explicit refresh.

- Acceptance Criteria:
    - A documented Glance widget configuration can render the current word data from `GET /word`.
    - A documented dashboard refresh control triggers word replacement via `POST /word/new` and updates the displayed `word_id`.
- Verification:
    - Integration artifact test: repository contains runnable Glance integration config and usage docs.
    - Manual smoke test: dashboard displays current word and refresh action results in a changed `word_id`.

### Non-Functional Requirements

NFR-1: The containerized service must be reachable by peer hosts on the local network.

- Acceptance Criteria:
    - Service binds to `0.0.0.0` and configured port (default `8080`).
    - With Docker port mapping enabled, peer host can receive HTTP 200 from `GET /health`.
- Verification:
    - Runtime smoke test: `docker compose up -d --build && curl http://<lan-host>:8080/health` from a peer host.

NFR-2: The API must meet baseline latency for local usage.

- Acceptance Criteria:
    - Under 20 concurrent clients over 60 seconds in a local network test, p95 latency is <= 150 ms for `GET /word`.
- Verification:
    - Load test command (example): `k6 run tests/perf/get_word.js` with reported threshold pass.

NFR-3: The service must emit structured logs for operational debugging.

- Acceptance Criteria:
    - Each request log includes `timestamp`, `method`, `path`, `status_code`, `request_id`, and `latency_ms`.
    - Cycle-reset events include `event=cycle_reset` and resulting `cycle_id`.
- Verification:
    - Unit/integration logging tests: `pytest -q tests/unit/test_logging_schema.py`.
    - Manual log inspection in container output for cycle reset scenario.

NFR-4: CI must run automated quality gates on each pull request.

- Acceptance Criteria:
    - GitHub Actions runs unit + integration tests and fails pipeline on test failure.
    - Docker image build step runs successfully in CI.
- Verification:
    - CI workflow execution signal on PR (`pass` required).

NFR-5: Glance integration assets must be reproducible for self-hosted deployment.

- Acceptance Criteria:
    - Repository includes an example Glance page/widget config and brief setup instructions.
    - Integration example uses only local-network addresses and no external runtime dependencies.
- Verification:
    - Documentation check: integration files exist under version control and pass YAML validation.
    - Manual verification against local Docker deployment.

## Edge Cases and Failure Modes

- Dataset file missing at startup -> service fails fast and returns `DATASET_UNAVAILABLE` on API calls.
- SQLite volume is read-only or unavailable -> `/health` degrades and write operations return `DB_UNAVAILABLE`.
- Dataset exhaustion within cycle -> cycle increments and generation resumes without duplicate inside same cycle.
- Baseline seed list references words not present in current dataset -> service skips unmatched seed entries and logs seed mismatch count.
- Concurrent `POST /word/new` calls -> transactional write ensures single active word and no duplicate assignment.
- Dashboard refresh invoked while DB is degraded -> refresh control surfaces deterministic error response and leaves previous displayed word unchanged.

## Observability

- Logs: Structured JSON request logs and explicit lifecycle events (`word_generated`, `word_replaced`, `cycle_reset`, error codes).
- Metrics: Request count, request latency histogram, error count by `error_code`, and current `cycle_id` gauge.
- Metrics: Include per-endpoint request counts so dashboard refresh traffic can be distinguished from read traffic.
- Alerts: Trigger when `/health` is degraded for 5 consecutive checks or error rate exceeds 5% over 10 minutes.

## Phasing Plan

| Phase | Requirements (IDs) | Scope | Exit Criteria (verifiable) | Deferred |
| --- | --- | --- | --- | --- |
| 0-lan-health-harness | FR-4, NFR-1, NFR-4 | Deliver runnable Dockerized FastAPI service with `/health`, SQLite connectivity check, and CI workflow skeleton. | `docker compose up -d --build` succeeds; `GET /health` returns 200 in healthy state; DB-failure test returns 503; CI runs tests on PR. | Word generation endpoints and dedup logic. |
| 1-active-word-read-path | FR-1, FR-5 | Implement dataset loading and `GET /word` read path with deterministic error contracts. | `pytest -q tests/integration/test_get_word.py` passes; required response fields present; DB unavailable returns 503 + `DB_UNAVAILABLE`; dataset load failure returns 500 + `DATASET_UNAVAILABLE`. | Forced refresh and cycle-exhaustion handling. |
| 2-unique-refresh-cycle | FR-2, FR-3 | Add `POST /word/new`, persistent used-word tracking, baseline top-500 seed initialization, and cycle reset semantics. | `pytest -q tests/integration/test_new_word.py` passes; seed test validates baseline IDs are pre-used; no duplicate `word_id` before exhaustion; cycle increments on exhaustion; post-refresh `GET /word` returns new active word. | Performance tuning and advanced observability. |
| 3-observability-and-latency | NFR-2, NFR-3 | Add structured logging schema, cycle reset event logging, and baseline load-test coverage. | Log schema tests pass; cycle reset log event appears with `cycle_id`; load test shows p95 <= 150 ms for `GET /word` at defined load. | Internet exposure, authentication, and UI. |
| 4-glance-dashboard-integration | FR-6, NFR-5 | Add runnable Glance integration assets and docs for display + refresh workflows. | Example Glance config renders current word; refresh control triggers `POST /word/new` and updates visible `word_id`; integration docs validated locally. | Custom Glance plugin development. |

## Rollout Plan

- Release strategy: Deploy container to local host, expose mapped port on LAN, and allow consumers to migrate to `GET /word` then `POST /word/new`.
- Rollback plan: Redeploy previous image tag and preserve SQLite volume snapshot; if schema changes are introduced later, include reversible migration scripts.

## Open Questions

- Open questions are tracked in [the decision log](decision-log.md) and currently include dataset licensing/provenance confirmation.

## Decision Log

Track the full decision history in [the decision log](decision-log.md).

## Glossary

Canonical term definitions are maintained in [the glossary](glossary.md).

## Diagrams

Store Mermaid diagrams as separate Markdown files under `docs/spec/<prd-slug>/diagrams/` (one diagram per file). Reference diagrams from the relevant sections using relative paths.

- [user flow: fetch and refresh](diagrams/01-user-flow-word-fetch-and-refresh.md): Client behavior for read and force-new paths with failure branches.
- [API sequence: generate and persist](diagrams/02-api-sequence-generate-and-persist-word.md): Service, SQLite, and dataset interactions.
- [domain state: cycle lifecycle](diagrams/03-domain-state-word-cycle-lifecycle.md): Active-word and cycle-exhaustion lifecycle.

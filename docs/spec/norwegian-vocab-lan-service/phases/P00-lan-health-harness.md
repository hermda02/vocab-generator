# Phase 0: LAN Health Harness

Deliver a runnable Dockerized FastAPI service with SQLite readiness checks and CI wiring.

## Exit Criteria

- [ ] `docker compose up -d --build` starts the service and healthcheck passes locally.
- [ ] `GET /health` returns HTTP 200 with `status=ok` when DB is reachable.
- [ ] `GET /health` returns HTTP 503 with `status=degraded` when DB is unavailable.
- [ ] GitHub Actions executes test workflow and Docker build on pull requests.

## Phase Handoff Summary

- [ ] Record final image/service names and exposed port for downstream phases.
- [ ] Record any environment variables required for local and CI runs.
- [ ] Record unresolved infra risks discovered in this phase.

## Task 1: P00-001 Bootstrap FastAPI Service Skeleton

Create initial Python/FastAPI application structure with entrypoint and dependency setup.

task_id: T001
Covers: FR-4, NFR-1
<!-- Omit Depends on when there are no dependencies. -->

- [ ] FastAPI app starts with `uvicorn` from container entrypoint.
- [ ] Source layout includes clear modules for API routes, services, and persistence.
- [ ] `README.md` includes a minimal local run command for developers.

### Implementation Notes

- [ ] _Implementation agent records file-level changes and rationale._

### Downstream Handoff Notes

- [ ] _Document project entrypoints and where later tasks should add endpoints._

### Follow-ups

- [ ] _List any package/version constraints discovered during bootstrap._

## Task 2: P00-002 Add SQLite Wiring and Readiness Probe

Implement SQLite connection management and a health service that reports DB connectivity.

task_id: T002
Covers: FR-4
Depends on: T001
<!-- Omit Depends on when there are no dependencies. -->

- [ ] SQLite connection opens from configured path and fails with explicit error on invalid path.
- [ ] Health service checks DB connectivity with a lightweight query.
- [ ] DB failure path is surfaced to caller as degraded readiness state.

### Implementation Notes

- [ ] _Implementation agent records schema/bootstrap decisions that affect later persistence tasks._

### Downstream Handoff Notes

- [ ] _Document DB path configuration and expected mounted volume path._

### Follow-ups

- [ ] _List migration or schema-hardening items deferred to later phases._

## Task 3: P00-003 Implement GET /health and Docker Healthcheck

Expose `GET /health` and wire Docker healthcheck to the endpoint for runtime readiness.

task_id: T003
Covers: FR-4, NFR-1
Depends on: T002
<!-- Omit Depends on when there are no dependencies. -->

- [ ] `GET /health` returns `200` + `{"status":"ok"}` when app and DB are healthy.
- [ ] `GET /health` returns `503` + `{"status":"degraded"}` when DB check fails.
- [ ] `docker-compose`/`Dockerfile` healthcheck probes `/health` successfully.

### Implementation Notes

- [ ] _Implementation agent records response contract details for reuse in tests._

### Downstream Handoff Notes

- [ ] _Document health endpoint behavior for LAN consumers and operators._

### Follow-ups

- [ ] _List any additional operational probes deferred to future work._

## Task 4: P00-004 Add CI Workflow for Tests and Image Build

Create GitHub Actions workflow that runs tests and Docker image build on PRs.

task_id: T004
Covers: NFR-4
Depends on: T001
<!-- Omit Depends on when there are no dependencies. -->

- [ ] CI workflow runs unit/integration test command and fails on test failures.
- [ ] CI workflow builds Docker image successfully using repository Docker config.
- [ ] Workflow triggers on pull requests to default branch.

### Implementation Notes

- [ ] _Implementation agent records exact CI commands and caching assumptions._

### Downstream Handoff Notes

- [ ] _Document required secrets/variables (if none, explicitly note none required)._

### Follow-ups

- [ ] _List performance optimizations for CI runtime, if discovered._

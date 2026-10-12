# Phase 1: Active Word Read Path

Deliver dataset-backed `GET /word` behavior with deterministic error contracts for read flows.

## Exit Criteria

- [ ] `GET /word` returns all required fields when creating the first active word.
- [ ] Repeated `GET /word` calls return the same active word until refresh endpoint is implemented.
- [ ] DB failures return HTTP 503 with `error_code=DB_UNAVAILABLE`.
- [ ] Dataset load failures return HTTP 500 with `error_code=DATASET_UNAVAILABLE`.

## Phase Handoff Summary

- [ ] Record dataset file format and validation rules for reuse in refresh/cycle tasks.
- [ ] Record response schema contract used by integration tests.
- [ ] Record known limitations before forced-refresh behavior is added.

## Task 5: P01-001 Define Dataset Contract and Loader

Implement static dataset schema validation and loader used by word selection services.

task_id: T005
Covers: FR-1, FR-5
Depends on: T001
<!-- Omit Depends on when there are no dependencies. -->

- [ ] Loader reads bundled dataset from repository path configured via app settings.
- [ ] Loader validates each entry includes `word_id`, Norwegian/English words, and both definitions.
- [ ] Loader failures raise a mapped application error that can produce `DATASET_UNAVAILABLE`.

### Implementation Notes

- [ ] _Implementation agent records dataset file path and schema assumptions._

### Downstream Handoff Notes

- [ ] _Document how later tasks access the loaded dataset safely._

### Follow-ups

- [ ] _List licensing/provenance checks that remain outside implementation scope._

## Task 6: P01-002 Persist and Retrieve Active Word State

Add persistence model/repository for active word so repeated reads return a stable result.

task_id: T006
Covers: FR-1
Depends on: T002, T005
<!-- Omit Depends on when there are no dependencies. -->

- [ ] Persistence layer supports read active word and upsert active word operations.
- [ ] Active word retrieval returns `None` when not yet initialized.
- [ ] Repository operations are covered by unit tests for success and empty-state behavior.

### Implementation Notes

- [ ] _Implementation agent records table/column names and constraints used._

### Downstream Handoff Notes

- [ ] _Document repository APIs that refresh/cycle logic must call._

### Follow-ups

- [ ] _List index or transaction improvements deferred to later phases._

## Task 7: P01-003 Implement GET /word Handler with First-Word Generation

Implement `GET /word` endpoint that returns existing active word or generates/persists first word when missing.

task_id: T007
Covers: FR-1
Depends on: T005, T006
<!-- Omit Depends on when there are no dependencies. -->

- [ ] Existing active word path returns HTTP 200 with required payload fields.
- [ ] No-active-word path selects one dataset entry, persists it as active, and returns HTTP 200.
- [ ] Endpoint includes `cycle_id` and `generated_at` in all successful responses.

### Implementation Notes

- [ ] _Implementation agent records endpoint contract and selection behavior._

### Downstream Handoff Notes

- [ ] _Document expected behavior that changes once `POST /word/new` is added._

### Follow-ups

- [ ] _List any endpoint-level TODOs intentionally deferred to phase 2._

## Task 8: P01-004 Implement Error Mapping and Integration Tests for Read Path

Map operational errors to deterministic response contracts and add integration coverage for `GET /word`.

task_id: T008
Covers: FR-1, FR-5
Depends on: T007
<!-- Omit Depends on when there are no dependencies. -->

- [ ] DB failure path returns HTTP 503 with `error_code=DB_UNAVAILABLE`.
- [ ] Dataset load failure path returns HTTP 500 with `error_code=DATASET_UNAVAILABLE`.
- [ ] `pytest -q tests/integration/test_get_word.py` and `pytest -q tests/integration/test_error_contracts.py` pass.

### Implementation Notes

- [ ] _Implementation agent records how failure scenarios are injected in tests._

### Downstream Handoff Notes

- [ ] _Document reusable test fixtures for phase 2 endpoint tests._

### Follow-ups

- [ ] _List additional failure-mode tests deferred to hardening work._

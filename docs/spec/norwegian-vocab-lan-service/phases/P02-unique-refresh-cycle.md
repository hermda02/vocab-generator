# Phase 2: Unique Refresh Cycle

Deliver forced-refresh behavior, baseline top-500 pre-used seeding, and no-duplicate selection within each dataset cycle.

## Exit Criteria

- [ ] `POST /word/new` replaces the active word and returns a different `word_id`.
- [ ] Initialization seeds the top-500 baseline list as already used (when entries are present in dataset mapping).
- [ ] No `word_id` repeats before cycle exhaustion using finite-dataset integration tests.
- [ ] Exhaustion increments `cycle_id` and generation resumes from full dataset.
- [ ] Concurrent refresh requests keep one consistent active-word state without duplicate assignment in a cycle.

## Phase Handoff Summary

- [ ] Record cycle-reset behavior and DB invariants for operators.
- [ ] Record concurrency assumptions and locking/transaction semantics.
- [ ] Record any known throughput constraints before observability/performance phase.

## Task 9: P02-001 Model Used-Word Tracking and Cycle Metadata

Add persistence structures for used words and cycle metadata required for uniqueness enforcement.

task_id: T009
Covers: FR-3
Depends on: T006
<!-- Omit Depends on when there are no dependencies. -->

- [ ] Schema/repository supports recording used words keyed by `cycle_id`.
- [ ] Repository supports reading current cycle and incrementing `cycle_id` atomically.
- [ ] Schema/repository supports one-time baseline seeding state so top-500 initialization is idempotent.
- [ ] DB tests verify uniqueness bookkeeping across inserts and cycle transitions.

### Implementation Notes

- [ ] _Implementation agent records schema choices and migration strategy (if any)._

### Downstream Handoff Notes

- [ ] _Document persistence APIs expected by selector and refresh endpoint logic._

### Follow-ups

- [ ] _List storage optimizations deferred for larger datasets._

## Task 10: P02-002 Implement Unique Selector with Exhaustion Reset

Implement word selection service that avoids used words in current cycle and performs reset on exhaustion.

task_id: T010
Covers: FR-3
Depends on: T005, T009
<!-- Omit Depends on when there are no dependencies. -->

- [ ] Selector excludes words marked used both by baseline top-500 seed and runtime usage.
- [ ] Exhaustion path increments `cycle_id` and selects from full dataset for new cycle.
- [ ] Cycle reset emits a domain event payload containing `cycle_id` for logging.

### Implementation Notes

- [ ] _Implementation agent records deterministic selection/testing strategy for finite fixtures._

### Downstream Handoff Notes

- [ ] _Document selector interface reused by both GET and POST flows._

### Follow-ups

- [ ] _List any randomness-quality concerns deferred to future tuning._

## Task 11: P02-003 Implement POST /word/new Transactional Refresh

Implement endpoint flow that marks previous active word used, selects next unique word, persists active word, and returns payload.

task_id: T011
Covers: FR-2, FR-3
Depends on: T007, T009, T010
<!-- Omit Depends on when there are no dependencies. -->

- [ ] `POST /word/new` returns HTTP 200 with required payload fields and new `word_id`.
- [ ] Previous active word is recorded as used within the same transactional unit as active-word replacement.
- [ ] Subsequent `GET /word` returns the refreshed active word.

### Implementation Notes

- [ ] _Implementation agent records transaction boundaries and conflict handling approach._

### Downstream Handoff Notes

- [ ] _Document endpoint behavior and idempotency expectations for clients._

### Follow-ups

- [ ] _List additional retry/backoff behaviors deferred beyond current scope._

## Task 12: P02-004 Add Integration and Concurrency Tests for Refresh/Cycle Logic

Add integration coverage for refresh, uniqueness, cycle reset, and concurrent refresh safety.

task_id: T012
Covers: FR-2, FR-3
Depends on: T011
<!-- Omit Depends on when there are no dependencies. -->

- [ ] `pytest -q tests/integration/test_new_word.py` passes.
- [ ] `pytest -q tests/integration/test_uniqueness_cycle.py` passes with no duplicates pre-exhaustion.
- [ ] `pytest -q tests/integration/test_seed_used_words.py` passes for top-500 baseline seeding behavior.
- [ ] Concurrency scenario test demonstrates consistent active-word state and no duplicate assignment in a cycle.

### Implementation Notes

- [ ] _Implementation agent records fixture sizes and concurrency test harness setup._

### Downstream Handoff Notes

- [ ] _Document reusable assertions and fixtures for observability/perf tests._

### Follow-ups

- [ ] _List stress-test scenarios deferred to NFR latency phase._

# Phase 3: Observability and Latency

Deliver structured telemetry, operational alerts, and baseline latency verification for LAN usage.

## Exit Criteria

- [ ] Structured request logs include required fields for all API routes.
- [ ] Domain events include `word_generated`, `word_replaced`, and `cycle_reset` with required metadata.
- [ ] Metrics expose request count, latency histogram, error count by code, and current cycle gauge.
- [ ] Load test demonstrates p95 <= 150 ms for `GET /word` under the defined local workload.

## Phase Handoff Summary

- [ ] Record telemetry field dictionary and metric names for operators.
- [ ] Record alert thresholds and where alert evaluation is configured.
- [ ] Record baseline performance results and test environment assumptions.

## Task 13: P03-001 Add Structured Request Logging Middleware

Implement request logging middleware with required schema and correlation fields.

task_id: T013
Covers: NFR-3
Depends on: T003, T011
<!-- Omit Depends on when there are no dependencies. -->

- [ ] Each API request emits one log record including `timestamp`, `method`, `path`, `status_code`, `request_id`, and `latency_ms`.
- [ ] Error responses include machine-readable `error_code` in logs when present.
- [ ] `pytest -q tests/unit/test_logging_schema.py` passes for request log schema checks.

### Implementation Notes

- [ ] _Implementation agent records log format/version to protect downstream parsers._

### Downstream Handoff Notes

- [ ] _Document how consumers correlate request IDs across logs and client traces._

### Follow-ups

- [ ] _List optional log redaction/retention policies outside current PRD scope._

## Task 14: P03-002 Emit Domain Event Logs and Metrics

Emit lifecycle event logs and metrics for generation, replacement, failures, and cycle state.

task_id: T014
Covers: NFR-3
Depends on: T010, T011, T013
<!-- Omit Depends on when there are no dependencies. -->

- [ ] Event logs include `word_generated`, `word_replaced`, and `cycle_reset` with relevant IDs.
- [ ] Metrics include request count, latency histogram, error count by `error_code`, and `cycle_id` gauge.
- [ ] Integration test validates cycle reset event presence with `cycle_id` in logs.

### Implementation Notes

- [ ] _Implementation agent records metric names/labels and emission points._

### Downstream Handoff Notes

- [ ] _Document how alerts/dashboards should consume metric and event streams._

### Follow-ups

- [ ] _List dashboard implementation work deferred if not required in-code._

## Task 15: P03-003 Define Health/Error Alert Rules and Operator Runbook

Document and implement alert rule configuration for prolonged degraded health and elevated error rate.

task_id: T015
Covers: NFR-3
Depends on: T014
<!-- Omit Depends on when there are no dependencies. -->

- [ ] Alert definition exists for `/health` degraded state over 5 consecutive checks.
- [ ] Alert definition exists for API error rate >5% over 10 minutes.
- [ ] Operator-facing runbook documents initial triage steps and rollback trigger points.

### Implementation Notes

- [ ] _Implementation agent records where alert rules live in-repo and deployment assumptions._

### Downstream Handoff Notes

- [ ] _Document ownership/escalation expectations for alert responders._

### Follow-ups

- [ ] _List additional SLO/SLA monitoring enhancements deferred to future iterations._

## Task 16: P03-004 Add Load Test and Enforce Latency Threshold

Add performance test assets and validate `GET /word` latency threshold under PRD workload.

task_id: T016
Covers: NFR-2
Depends on: T011, T014
<!-- Omit Depends on when there are no dependencies. -->

- [ ] `tests/perf/get_word.js` (or equivalent) defines 20-client, 60-second workload for `GET /word`.
- [ ] Load test command `k6 run tests/perf/get_word.js` reports p95 <= 150 ms.
- [ ] CI or documented manual verification path captures latency result artifact.

### Implementation Notes

- [ ] _Implementation agent records host/test conditions used for baseline measurement._

### Downstream Handoff Notes

- [ ] _Document how to rerun performance checks after future feature changes._

### Follow-ups

- [ ] _List optimization backlog items if threshold is only narrowly met._

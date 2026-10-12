# Phase 4: Glance Dashboard Integration

Deliver reproducible `glance-app` integration assets so the dashboard can display and refresh vocabulary entries.

## Exit Criteria

- [x] Repository contains a runnable Glance widget/page config that displays data from `GET /word`.
- [x] Dashboard refresh control triggers `POST /word/new` and updates visible `word_id`.
- [x] Integration guide documents local-network setup steps and expected behavior.
- [x] Integration smoke validation is documented with concrete commands and outcomes.

## Phase Handoff Summary

- [x] Record exact Glance widget mechanism used for refresh and why it was selected.
- [x] Record any Glance version assumptions for config compatibility.
- [x] Record known UX/interaction limitations for future enhancement.

## Task 17: P04-001 Add Versioned Glance Integration Assets

Add repository-managed Glance configuration files that render current word data from the service.

task_id: T017
Covers: FR-6, NFR-5
Depends on: T011
<!-- Omit Depends on when there are no dependencies. -->

- [x] Add example Glance config under `deploy/glance/` (or equivalent) with a widget that reads `GET /word`.
- [x] Widget rendering includes Norwegian/English words and both definitions.
- [x] Config references LAN-local service address placeholders that can be overridden by environment variables.

### Implementation Notes

- [x] Files: `deploy/glance/glance.yml`, `deploy/glance/pages/vocabulary.yml`; widget types: `custom-api` for display/health and `html` for refresh.

### Downstream Handoff Notes

- [x] Required edits documented in `deploy/glance/README.md` and `docs/operations/glance-integration-smoke-test.md`.

### Follow-ups

- [x] Deferred: custom CSS/theming improvements remain optional and out of scope.

## Task 18: P04-002 Implement and Validate Dashboard Refresh Control

Implement the refresh action path in Glance configuration so users can request a new word from the dashboard.

task_id: T018
Covers: FR-6
Depends on: T017
<!-- Omit Depends on when there are no dependencies. -->

- [x] Glance integration includes a user-triggered control that invokes `POST /word/new`.
- [x] After refresh action, displayed `word_id` changes and UI reflects the new entry.
- [x] Failure behavior on refresh uses existing deterministic error contract and is documented.

### Implementation Notes

- [x] Wiring uses HTML form submit to `POST /word/new` + delayed page reload to re-fetch current word.

### Downstream Handoff Notes

- [x] Troubleshooting documented in `docs/operations/glance-integration-smoke-test.md`.

### Follow-ups

- [x] Limitation recorded: no native action callback used; form+reload may motivate future dedicated refresh view endpoint.

## Task 19: P04-003 Document and Smoke-Test Glance End-to-End Setup

Add concise setup documentation and a repeatable local smoke test for dashboard display + refresh.

task_id: T019
Covers: FR-6, NFR-5
Depends on: T017, T018
<!-- Omit Depends on when there are no dependencies. -->

- [x] Add setup guide that includes service startup, Glance startup, and wiring of host/port values.
- [x] Smoke test checklist verifies initial word display and post-refresh word change.
- [x] Docs include expected signals (HTTP responses, visible dashboard output) for pass/fail validation.

### Implementation Notes

- [x] Commands recorded in `scripts/smoke_glance_integration.sh` and `docs/operations/glance-integration-smoke-test.md`.

### Downstream Handoff Notes

- [x] Update locations documented: `deploy/glance/pages/vocabulary.yml` and runbook references.

### Follow-ups

- [x] Follow-up: run shell smoke script in CI against ephemeral compose stack when Docker-in-CI resources allow.

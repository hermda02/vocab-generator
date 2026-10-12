# Phase 4: Glance Dashboard Integration

Deliver reproducible `glance-app` integration assets so the dashboard can display and refresh vocabulary entries.

## Exit Criteria

- [ ] Repository contains a runnable Glance widget/page config that displays data from `GET /word`.
- [ ] Dashboard refresh control triggers `POST /word/new` and updates visible `word_id`.
- [ ] Integration guide documents local-network setup steps and expected behavior.
- [ ] Integration smoke validation is documented with concrete commands and outcomes.

## Phase Handoff Summary

- [ ] Record exact Glance widget mechanism used for refresh and why it was selected.
- [ ] Record any Glance version assumptions for config compatibility.
- [ ] Record known UX/interaction limitations for future enhancement.

## Task 17: P04-001 Add Versioned Glance Integration Assets

Add repository-managed Glance configuration files that render current word data from the service.

task_id: T017
Covers: FR-6, NFR-5
Depends on: T011
<!-- Omit Depends on when there are no dependencies. -->

- [ ] Add example Glance config under `deploy/glance/` (or equivalent) with a widget that reads `GET /word`.
- [ ] Widget rendering includes Norwegian/English words and both definitions.
- [ ] Config references LAN-local service address placeholders that can be overridden by environment variables.

### Implementation Notes

- [ ] _Implementation agent records files/paths added and Glance widget type used._

### Downstream Handoff Notes

- [ ] _Document required edits users must make before using the example config._

### Follow-ups

- [ ] _List optional visual styling improvements outside core integration scope._

## Task 18: P04-002 Implement and Validate Dashboard Refresh Control

Implement the refresh action path in Glance configuration so users can request a new word from the dashboard.

task_id: T018
Covers: FR-6
Depends on: T017
<!-- Omit Depends on when there are no dependencies. -->

- [ ] Glance integration includes a user-triggered control that invokes `POST /word/new`.
- [ ] After refresh action, displayed `word_id` changes and UI reflects the new entry.
- [ ] Failure behavior on refresh uses existing deterministic error contract and is documented.

### Implementation Notes

- [ ] _Implementation agent records how Glance action wiring triggers refresh in practice._

### Downstream Handoff Notes

- [ ] _Document troubleshooting steps when refresh action does not update the widget._

### Follow-ups

- [ ] _List any Glance-side limitations that would motivate future endpoint variants._

## Task 19: P04-003 Document and Smoke-Test Glance End-to-End Setup

Add concise setup documentation and a repeatable local smoke test for dashboard display + refresh.

task_id: T019
Covers: FR-6, NFR-5
Depends on: T017, T018
<!-- Omit Depends on when there are no dependencies. -->

- [ ] Add setup guide that includes service startup, Glance startup, and wiring of host/port values.
- [ ] Smoke test checklist verifies initial word display and post-refresh word change.
- [ ] Docs include expected signals (HTTP responses, visible dashboard output) for pass/fail validation.

### Implementation Notes

- [ ] _Implementation agent records exact smoke test commands used._

### Downstream Handoff Notes

- [ ] _Document where to update integration files when API contract changes._

### Follow-ups

- [ ] _List automation opportunities for converting manual smoke test to CI in future._

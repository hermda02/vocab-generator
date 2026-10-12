# Decision Log - norwegian-vocab-lan-service

## Discovery and Alignment

Date: 2026-10-12

### Confirmed Decisions

1. Service interface
   - Decision: REST HTTP with JSON.
   - Chosen option: 1A.
   - Rationale: Simple interoperability for local-network services.

2. Runtime/language
   - Decision: Python with FastAPI.
   - Chosen option: 2A.
   - Rationale: Fast implementation path and straightforward API testing.

3. Vocabulary source
   - Decision: Bundled static dataset in the repository (offline).
   - Chosen option: 3A.
   - Rationale: Deterministic behavior and no runtime dependency on external APIs.

4. Duplicate prevention
   - Decision: Global uniqueness until dataset exhaustion, then reset in a new cycle.
   - Chosen option: 4A.
   - Rationale: Guarantees no repeats within a full cycle.

5. Data store
   - Decision: SQLite persisted on a mounted volume.
   - Chosen option: 5A.
   - Rationale: Minimal operations overhead while surviving container restarts.

6. "Request new word" semantics
   - Decision: Requesting replacement marks the previous word as used.
   - Chosen option: 6A.
   - Rationale: Preserves anti-duplicate guarantees.

7. LAN access/security
   - Decision: No auth; bind to 0.0.0.0 for trusted local network use.
   - Chosen option: 7A.
   - Rationale: Prioritizes low-friction local integration.

8. Verification and CI
   - Decision: pytest + API integration tests + Docker healthcheck in GitHub Actions.
   - Chosen option: 8A.
   - Rationale: Provides reproducible machine-verifiable quality gates.

9. Dashboard integration target
   - Decision: Service must integrate with `glance-app` to display the current word and allow user-triggered refresh.
   - Rationale: This service will be consumed from a self-hosted dashboard workflow.

10. Baseline pre-used vocabulary
   - Decision: Treat the 500 most common Norwegian words as already used at initialization.
   - Source: https://www.korrekturavdelingen.no/ord-uttrykk-frekvensordliste-500-vanligste-norsk.htm
   - Rationale: Generation should start beyond the most common beginner words.

### Tradeoffs Captured

- No-auth LAN model is simple but should only run on trusted networks.
- Offline static dataset improves reliability but requires explicit dataset curation updates.
- SQLite is operationally simple but not intended for high-write multi-node workloads.

## Assumptions to Validate During Drafting

- API shape will include a read endpoint for current word and a separate endpoint for forced replacement.
- A cycle reset after dataset exhaustion will be explicit in metadata and logs.
- Definitions are provided in both Norwegian and English for each generated entry.

## Open Questions (Parked)

1. Dataset provenance and licensing
   - Why open: The source and redistribution rights for Norwegian-English definitions are not yet specified.
   - Follow-up plan: Select and document an approved dataset source before implementation begins.

2. Cardinality of language fields
   - Why open: The phrase "their definitions (in both languages)" can mean one or multiple definitions per language.
   - Follow-up plan: Default to one primary definition per language in phase 1; revisit if richer dictionary entries are required.

3. Glance widget mechanism for refresh button
   - Why open: Glance offers multiple integration methods (`custom-api`, `extension`, `iframe`) with different support for interactive actions.
   - Follow-up plan: In implementation phase, validate and document the exact widget pattern used to trigger `POST /word/new` from a dashboard button.

4. Top-500 source normalization and licensing
   - Why open: The source page is human-readable HTML; implementation needs a reproducible normalized seed file and explicit attribution/licensing note.
   - Follow-up plan: During phase 2, store a versioned normalized seed file in-repo and document provenance/attribution in project docs.

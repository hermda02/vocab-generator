# Glossary - norwegian-vocab-lan-service

## Terms

- **Active Word**: The currently selected vocabulary entry returned by `GET /word` until `POST /word/new` replaces it.
- **Vocabulary Entry**: A single record containing `word_id`, Norwegian word, English word, Norwegian definition, and English definition.
- **Dataset Cycle**: The uniqueness window in which each `word_id` can appear at most once before reset.
- **Cycle Exhaustion**: The point where all dataset entries have been used in the current cycle.
- **Cycle Reset**: The action of incrementing `cycle_id` and restarting selection from the full dataset after exhaustion.
- **Used-Word State**: Persisted tracking data in SQLite indicating which words have already been served in the current cycle.
- **Forced Refresh**: A client-triggered call to `POST /word/new` that generates a new active word and marks the previous active word as used.
- **LAN Consumer**: A service or script on the trusted local network that calls this API.
- **Deterministic Error Contract**: A stable error response format that includes machine-readable codes such as `DB_UNAVAILABLE` and `DATASET_UNAVAILABLE`.
- **Readiness**: Service health state based on API process availability and SQLite connectivity, exposed by `GET /health`.
- **Glance Integration**: A dashboard-consumption contract using `glance-app` to display the current active word and trigger explicit refresh.
- **Dashboard Refresh Control**: A user-facing control in Glance that invokes `POST /word/new` and then updates displayed word data.
- **Baseline Used Set**: The seed set of the 500 most common Norwegian words that are marked as used on initialization before normal random generation.

## Canonical Event Names

- `word_generated`: Logged when a word is selected and persisted.
- `word_replaced`: Logged when `POST /word/new` replaces the active word.
- `cycle_reset`: Logged when cycle exhaustion triggers a reset.

## Notes

- This glossary is derived from definitions in `prd.md` and should be updated whenever requirement wording changes.

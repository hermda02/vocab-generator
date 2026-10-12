# Glance Integration Smoke Test

This runbook validates both:

- the local container service behavior (`GET /word`, `POST /word/new`)
- the Glance dashboard integration (`deploy/glance/*`)

## 1) Container/API smoke test

Run from this repository:

```bash
./scripts/smoke_glance_integration.sh
```

Expected pass signals:

- script prints `PASS: refresh changed word_id`
- script prints `PASS: container API smoke test completed`

## 2) Glance configuration install (remote server)

On the Glance host:

1. Copy `deploy/glance/glance.yml` and `deploy/glance/pages/vocabulary.yml` into your Glance config directory.
2. Ensure `pages/vocabulary.yml` is reachable by the include path used in `glance.yml`.
3. Set env vars for Glance process:
   - `VOCAB_API_INTERNAL_URL` (reachable from Glance server)
   - `VOCAB_API_BROWSER_URL` (reachable from browser)
4. Reload/restart Glance.

## 3) Dashboard behavior verification

Open the Glance "Vocabulary" page and verify:

- current word widget shows Norwegian word, English equivalent, and both definitions
- health widget shows `status: ok` under normal conditions
- clicking `Generate New Word` updates displayed `word_id`

Pass/fail criteria:

- Pass if refresh changes `word_id` and no error page appears in Glance.
- Fail if refresh does not change `word_id` after page reload or health is degraded.

## 4) Troubleshooting

- If widgets are empty, check `VOCAB_API_INTERNAL_URL` accessibility from Glance host.
- If refresh fails but display works, check `VOCAB_API_BROWSER_URL` accessibility from browser network.
- If status is degraded, inspect vocab service logs and `/health` response.

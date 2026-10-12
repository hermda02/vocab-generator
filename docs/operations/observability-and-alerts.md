# Observability and Alerts Runbook

## Telemetry Field Dictionary

- Request logs (`event=request`) include:
  - `timestamp`
  - `method`
  - `path`
  - `status_code`
  - `request_id`
  - `latency_ms`
  - `error_code` (when error response includes one)
- Domain events:
  - `word_generated` with `word_id`, `cycle_id`
  - `word_replaced` with `word_id`, `cycle_id`
  - `cycle_reset` with `cycle_id`
- Metrics endpoint: `GET /metrics`
  - `request_count_by_endpoint`
  - `request_latency_histogram_ms`
  - `error_count_by_code`
  - `current_cycle_id`

## Alert Definitions

- Health degradation alert:
  - Condition: `GET /health` reports degraded status for 5 consecutive checks.
  - Suggested cadence: every 30 seconds.
  - Severity: warning.
- Error rate alert:
  - Condition: error responses / total responses > 5% over a rolling 10-minute window.
  - Source: request logs (`status_code >= 500`) or metrics (`error_count_by_code`).
  - Severity: critical.

## Triage Steps

1. Check recent request logs for `error_code` spikes.
2. Check `/metrics` for endpoint-specific request volume and current cycle gauge.
3. Validate DB mount accessibility (`DB_PATH`) and dataset/seed file accessibility.
4. If cycle-reset activity appears excessive, validate dataset size and used-word growth.

## Baseline Latency Validation

Run against a local deployment:

```bash
docker compose up -d --build
k6 run tests/perf/get_word.js
```

Pass condition: `p(95) <= 150ms` on `http_req_duration`.

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial product specification package with PRD, decision log, diagrams, glossary, and phased implementation plans.
- Glance integration assets under `deploy/glance/` with dashboard display and refresh wiring.
- Python/FastAPI service with endpoints for health (`GET /health`), active word retrieval (`GET /word`), refresh (`POST /word/new`), and telemetry (`GET /metrics`).
- Static vocabulary dataset support and baseline pre-used seed list support.
- SQLite persistence for active word state, used-word tracking, cycle metadata, and baseline seed initialization.
- Structured request logging and domain event logging (`word_generated`, `word_replaced`, `cycle_reset`).
- In-memory telemetry metrics for request counts, latency histogram buckets, error codes, and cycle gauge.
- Integration and unit test coverage for API contracts, cycle behavior, seed behavior, observability, and Glance asset wiring.
- Load-test script for `GET /word` latency threshold validation (`tests/perf/get_word.js`).
- Operations runbooks for observability/alerts and Glance integration smoke testing.

### Changed

- README updated to describe project overview and functionality.

[Unreleased]: https://github.com/hermda02/vocab-generator/compare/main...HEAD

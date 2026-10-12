# Glance Integration Example

This directory contains a runnable Glance configuration example for the
Norwegian Vocabulary LAN service.

## Files

- `glance.yml`: Top-level Glance config.
- `pages/vocabulary.yml`: Dashboard page with:
  - current word display (`GET /word`)
  - refresh button (`POST /word/new`)
  - service health display (`GET /health`)

## Required environment variables

- `VOCAB_API_INTERNAL_URL`: API base URL reachable from the Glance server/container.
  - Example: `http://vocab-generator:8080`
- `VOCAB_API_BROWSER_URL`: API base URL reachable from the end user's browser.
  - Example: `http://192.168.1.20:8080`

These can be the same URL in simple LAN setups.

## Notes

- The refresh control uses an HTML form submit to avoid browser-side CORS
  complexity for cross-origin `fetch`.
- After submit, the page reloads so the word widget re-reads `GET /word`.

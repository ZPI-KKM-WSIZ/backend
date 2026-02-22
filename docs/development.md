# Development Guide

## Local Setup

```bash
poetry install
poetry shell
```

## Running Tests

> ⚠️ Test suites are scaffolded but not yet implemented.

```bash
pytest
```

| Path                              | Scope                                                     |
|-----------------------------------|-----------------------------------------------------------|
| `tests/unit/core/`                | Infrastructure — Cassandra service, Tailscale, env config |
| `tests/unit/fast_api/services/`   | Business logic — readings & identity services             |
| `tests/unit/fast_api/exceptions/` | Exception handler behaviour                               |
| `tests/unit/integration/api/`     | API endpoint integration (health, readings)               |
| `tests/unit/integration/`         | Database flow integration                                 |
| `tests/e2e/`                      | Full sensor ingestion pipeline                            |

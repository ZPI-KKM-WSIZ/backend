# ZPI Air Quality — Backend Node

> [!WARNING]
> **Early Development** — APIs, configuration, and documentation are actively changing.

A stateless FastAPI backend node for the ZPI Air Quality monitoring system. It ingests sensor readings from registered
devices, persists them to a distributed Cassandra database, and serves a REST API consumed by the frontend. Built for
containerised deployment with zero-config horizontal replication via Cloudflare Tunnel and location-independent database
discovery via Tailscale.

---

## Architecture

```
   [Sensors] ──┐
               ▼
        [Public Domain] <───> [Frontend]
               │
        ┌──────┴──────┐
        ▼             ▼
  Backend Node   Backend Node ← stateless, replicable
        └──────┬──────┘
               │ [Tailscale VPN]
               ▼
      [Cassandra Cluster]

```

**Data flow:**

1. Sensors push `SensorReadingDTO` payloads to the public API domain
2. A backend node receives, validates, and converts the DTO into a database model
3. The model is handed off to the `cassandra-repositories` library for persistence
4. The frontend reads aggregated data via the same public API domain

Each node is **fully stateless** — multiple identical instances can run simultaneously. Cloudflare Tunnel handles load
balancing and high availability across nodes. Each node auto-generates a unique `SERVER_ID` at startup so individual
replicas remain identifiable.

---

## Project Structure

```
.
├── src/
│ ├── main.py # Entry point
│ ├── core/ # Infrastructure layer
│ │ ├── basic_configuration.py # Pydantic settings — env vars + .env file
│ │ ├── bootstrap_utils.py # App version resolution from pyproject.toml
│ │ ├── cassandra_service.py # Cassandra cluster connection & session lifecycle
│ │ ├── database_repositories.py # Repository container for dependency injection
│ │ ├── environment.py # Environment enum (PRODUCTION / DEVELOPMENT)
│ │ ├── identity_configuration.py # Server identity dataclass
│ │ ├── location_utils.py # Reverse geocoding via geopy/Nominatim
│ │ ├── logger_configuration.py # Coloured logger (level adapts to environment)
│ │ ├── network_utils.py # Async retry with exponential backoff + jitter
│ │ └── tailscale_service.py # Tailscale API client for Cassandra node discovery
│ └── fast_api/ # API layer
│ ├── api/v1/endpoints/ # Route handlers (health, readings, ...)
│ ├── exceptions/ # Structured app exceptions mapped to HTTP status codes
│ ├── services/ # Business logic (reading ingestion, identity)
│ ├── application_context.py # App-wide shared state
│ ├── dependencies.py # FastAPI dependency injection providers
│ ├── exception_handler.py # Global exception → HTTP response mapping
│ ├── fastapi_factory.py # Application factory / bootstrapping
│ ├── fastapi_settings.py # FastAPI-specific settings
│ └── router.py # Top-level router registration
├── tests/
│ ├── e2e/ # End-to-end tests
│ ├── unit/core/ # Unit tests — infrastructure layer
│ ├── unit/fast_api/ # Unit tests — API layer
│ ├── unit/integration/ # Integration tests (API + DB flow)
│ └── mocks/ # Shared test doubles
├── docs/ # Detailed documentation
├── scripts/
│ └── ts-healthcheck.sh # Tailscale peer connectivity healthcheck
├── docker-compose.dev.yaml
├── docker-compose.test.yaml
├── docker-compose.prod.yaml
├── compose.test.sh # Launches test stack (auto-generates SERVER_ID)
├── compose.prod.sh # Launches prod stack (auto-generates SERVER_ID)
├── Dockerfile
└── pyproject.toml
```

---

## Prerequisites

- **Docker** and **Docker Compose** v2+
- **Python 3.13** with **Poetry** (local development only)
- A **Tailscale** account with an OAuth client (`devices:read` scope)
- A **Cloudflare Tunnel** token (production / test deployments)
- A **Cassandra** node running on your Tailscale network, tagged appropriately —
  see [Deployment Guide](docs/deployment.md#tailscale-setup)

---

## Quick Start

```bash
# Build the Docker image
docker build --secret="id=env,src=.env" -t zpi-kkm-backend:${APP_VERSION} .

# Production — auto-generates SERVER_ID and BACKEND_HOSTNAME
bash compose.prod.sh

# Test environment — auto-generates SERVER_ID and BACKEND_HOSTNAME
bash compose.test.sh

# Dev (local, no tunnel)
docker compose -f docker-compose.dev.yaml up
```

> [!NOTE]
> `compose.prod.sh` and `compose.test.sh` automatically generate a short UUID for `SERVER_ID` and derive
`BACKEND_HOSTNAME` from it (`zpi-backend-<uuid>`). All other variables must be set in your environment or a
> root-level `.env` before running — see Configuration.

See the [Deployment Guide](docs/deployment.md) for environment variables, Tailscale setup, and Cloudflare Tunnel
configuration.

---

## Documentation

| Document          | Description                                                     |
|-------------------|-----------------------------------------------------------------|
| Configuration     | All environment variables and `.env` settings                   |
| Deployment Guide  | Docker Compose workflows, Tailscale and Cloudflare Tunnel setup |
| API Reference     | Available endpoints                                             |
| Development Guide | Local setup and testing                                         |

---

## Key Dependencies

| Package                  | Version  | Notes                                                       |
|--------------------------|----------|-------------------------------------------------------------|
| `fastapi`                | `^0.128` | Web framework                                               |
| `uvicorn`                | `^0.40`  | ASGI server                                                 |
| `pydantic-settings`      | `^2.12`  | Settings and environment variable management                |
| `colorlog`               | `^6.10`  | Coloured log output                                         |
| `httpx`                  | `^0.28`  | Async HTTP client (Tailscale API calls)                     |
| `geopy`                  | `^2.4`   | Reverse geocoding for sensor location resolution            |
| `cassandra-repositories` | git      | CRUD repository abstractions for Cassandra — see note below |
| `pytest`                 | `^9.0`   | Test framework                                              |
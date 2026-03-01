# Configuration

Configuration is split between **Compose-level environment variables** and an **app-level `src/.env` file**.

The app uses [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) to load configuration.
Nested groups (`TAILSCALE`, `CASSANDRA`) are populated via the double-underscore delimiter (e.g.
`CASSANDRA__PORT=9042`).

---

## `src/.env` — App-Level Settings

> A full `src/.env.example` reference is coming. The tables below cover all supported variables.

### Identity & API

| Variable       | Default         | Description                                |
|----------------|-----------------|--------------------------------------------|
| `SERVER_ID`    | **required**    | Unique identifier for this server instance |
| `APP_NAME`     | `Air info Node` | Application display name                   |
| `ENVIRONMENT`  | `production`    | `production` or `development`              |
| `API_BASE_URL` | **required**    | Public base URL for FastAPI                |
| `API_PORT`     | `8000`          | Port the FastAPI server listens on         |

### `CASSANDRA__*` — Cassandra Connection

| Variable                      | Default       | Description                           |
|-------------------------------|---------------|---------------------------------------|
| `CASSANDRA__USERNAME`         | `cassandra`   | Cassandra auth username               |
| `CASSANDRA__PASSWORD`         | `cassandra`   | Cassandra auth password               |
| `CASSANDRA__LOCAL_DATACENTER` | `datacenter1` | Cassandra local datacenter name       |
| `CASSANDRA__PORT`             | `9042`        | Cassandra port                        |
| `CASSANDRA__KEYSPACE`         | `air_info`    | Cassandra keyspace                    |
| `CASSANDRA__CONNECT_TIMEOUT`  | `5.0`         | Connection timeout in seconds         |
| `CASSANDRA__REQUEST_TIMEOUT`  | `10.0`        | Query timeout in seconds              |
| `CASSANDRA__COMPRESSION`      | `false`       | Enable Cassandra protocol compression |
| `CASSANDRA__PROTOCOL_VERSION` | `4` (V4)      | Cassandra native protocol version     |
| `CASSANDRA__SSL_CONTEXT`      | `null`        | SSL context (path or identifier)      |
| `CASSANDRA__SSL_OPTIONS`      | `null`        | Additional SSL options as a dict      |

### `TAILSCALE__*` — Tailscale OAuth

| Variable                                 | Default      | Description                       |
|------------------------------------------|--------------|-----------------------------------|
| `TAILSCALE__TAILSCALE_API_CLIENT_ID`     | **required** | Tailscale OAuth client ID         |
| `TAILSCALE__TAILSCALE_API_CLIENT_SECRET` | **required** | Tailscale OAuth client secret     |
| `TAILSCALE__TAILNET_ID`                  | **required** | Your Tailscale tailnet identifier |

---

## Compose Environment Variables

Set these in your shell or a root-level `.env` before running any Compose command. `SERVER_ID` and `BACKEND_HOSTNAME`
are handled automatically by the provided launch scripts.

| Variable                      | Required For   | Description                                       |
|-------------------------------|----------------|---------------------------------------------------|
| `APP_VERSION`                 | All            | Docker image tag                                  |
| `ENVIRONMENT`                 | All            | `production` or `development`                     |
| `API_BASE_URL`                | All            | Public base URL for FastAPI                       |
| `TAILNET_ID`                  | All            | Your Tailscale tailnet identifier                 |
| `TAILSCALE_API_CLIENT_ID`     | All            | Tailscale OAuth client ID                         |
| `TAILSCALE_API_CLIENT_SECRET` | All            | Tailscale OAuth client secret                     |
| `TAILSCALE_AUTH_KEY_PROD`     | `prod`         | Tailscale ephemeral auth key (production)         |
| `TAILSCALE_AUTH_KEY_TEST`     | `test`         | Tailscale ephemeral auth key (test)               |
| `CLOUDFLARE_TUNNEL_TOKEN`     | `prod`, `test` | Cloudflare Tunnel token                           |
| `SERVER_ID`                   | Auto           | Unique node ID — set automatically by scripts     |
| `BACKEND_HOSTNAME`            | Auto           | Tailscale hostname — set automatically by scripts |

---

## Log Levels

Logging verbosity is controlled automatically by the `ENVIRONMENT` setting:

| Environment   | Log Level |
|---------------|-----------|
| `production`  | `INFO`    |
| `development` | `DEBUG`   |

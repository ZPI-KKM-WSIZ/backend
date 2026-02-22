# Configuration

Configuration is split between **Compose-level environment variables** and an **app-level `src/.env` file**.

## `src/.env` — App & Cassandra Settings

> 📋 A full `src/.env.example` reference is coming. The table below covers the most relevant variables.

| Variable           | Default       | Description                           |
|--------------------|---------------|---------------------------------------|
| `USERNAME`         | `cassandra`   | Cassandra auth username               |
| `PASSWORD`         | `cassandra`   | Cassandra auth password               |
| `LOCAL_DATACENTER` | `datacenter1` | Cassandra local datacenter name       |
| `PORT`             | `9042`        | Cassandra port                        |
| `KEYSPACE`         | `air_info`    | Cassandra keyspace                    |
| `CONNECT_TIMEOUT`  | `5.0`         | Connection timeout in seconds         |
| `REQUEST_TIMEOUT`  | `10.0`        | Query timeout in seconds              |
| `COMPRESSION`      | `false`       | Enable Cassandra protocol compression |

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

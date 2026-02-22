# Deployment Guide

## Running the Application

### Production

```bash
bash compose.prod.sh
```

Starts three containers: **Tailscale** (tagged `tag:prod,tag:backend`) → **Backend** (sharing the Tailscale network
namespace) → **Cloudflared** (forwarding public traffic to the node). A unique `SERVER_ID` and `BACKEND_HOSTNAME` are
generated via `uuidgen` so each replica is identifiable.

### Test Environment

```bash
bash compose.test.sh
```

Identical stack but uses `tag:test` on the Tailscale container and a separate Cloudflare Tunnel token. This isolates the
test environment from production Cassandra nodes while keeping the same deployment topology.

### Development (local, no tunnel)

```bash
docker compose -f docker-compose.dev.yaml up
```

Runs only the backend container with port `8000` mapped to the host. No Tailscale sidecar or Cloudflared container —
intended for offline testing of the containerised image. The app still requires valid Tailscale OAuth credentials to
discover Cassandra nodes at startup.

---

### Tailscale Setup

For Tailscale setup guide see [tailscale.md](tailscale.md)

---

### Cloudflare Setup

For Cloudflare setup guide see [cloudflare.md](cloudflare.md)
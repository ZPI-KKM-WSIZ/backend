# Deployment Guide

## Running the Application

### Build the Docker image:

```bash
docker build --secret="id=env,src=.env" -t=zpi-kkm-backend . 
```

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

### Development (local)

```bash
python3 ./src/main.py
```

Pure python for initial testing.

---

### Tailscale Setup

For Tailscale setup guide see [tailscale.md](tailscale.md)

---

### Cloudflare Setup

For Cloudflare setup guide see [cloudflare.md](cloudflare.md)
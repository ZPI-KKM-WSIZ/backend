# Cloudflare Tunnel

Each deployment includes a `cloudflared` container sidecar. Configure your tunnel in the Cloudflare dashboard to point
to `http://tailscale:8000` — the tailnet container bridges both cloudflared and backend networks, so `tailscale`
resolves
correctly inside the tunnel container.

The only required step on the deployment side is providing a valid `CLOUDFLARE_TUNNEL_TOKEN`. Multiple nodes each carry
their own token and can point to the same Cloudflare Tunnel, which distributes traffic across them automatically.

> The backend itself has no direct Cloudflare coupling. In theory any reverse-proxy tunnel could be used by substituting
> the `cloudflared` service in the Compose file. Cloudflare Tunnel via `cloudflared` is the only officially tested
> configuration.

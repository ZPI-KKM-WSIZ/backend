#!/bin/sh
tailscale status --json | python3 -c "
import sys, json
data = json.load(sys.stdin)
peers = data.get('Peer', {})
active = any(p.get('CurAddr') or p.get('Relay') for p in peers.values())
sys.exit(0 if active else 1)
"

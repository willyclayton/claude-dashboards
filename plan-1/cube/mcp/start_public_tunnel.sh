#!/usr/bin/env bash
# Expose the Cube MCP wrapper to claude.ai through a Cloudflare quick tunnel, so a Claude Dashboard can read Cube live.
# What this publishes: anyone who has the printed URL (it contains a random secret) can query the Cube `sales` view:
# metrics and the modeled dimensions only; no raw SQL and no personal columns (they are not in the model).
# Run stop_public_tunnel.sh when done. Needs Cube running on :4000 and ~/.cube-mcp/tunnel/cloudflared.
set -euo pipefail
LAB="$(cd "$(dirname "$0")/.." && pwd)"
HOME_DIR="$HOME/.cube-mcp"
[ -x "$HOME_DIR/tunnel/cloudflared" ] || { echo "cloudflared not found in $HOME_DIR/tunnel"; exit 1; }
curl -s -o /dev/null http://localhost:4000/readyz || { echo "Cube is not running on :4000 (docker compose up -d)"; exit 1; }
cp "$LAB/mcp/server.py" "$HOME_DIR/server.py"
cp "$LAB/mcp/stop_public_tunnel.sh" "$HOME_DIR/stop_public_tunnel.sh"
# Only the API secret goes to the wrapper; the Snowflake token stays out of its environment.
CUBEJS_API_SECRET="$(grep '^CUBEJS_API_SECRET=' "$LAB/.env" | cut -d= -f2-)"; export CUBEJS_API_SECRET
"$HOME_DIR/stop_public_tunnel.sh" 2>/dev/null || true
SECRET="$(python3 -c 'import secrets;print(secrets.token_urlsafe(24))')"
# 1. open the tunnel first: its random hostname must be allowed by the wrapper (the MCP library answers other hosts with HTTP 421)
nohup "$HOME_DIR/tunnel/cloudflared" tunnel --no-autoupdate --url http://127.0.0.1:3001 > "$HOME_DIR/tunnel.log" 2>&1 &
echo $! > "$HOME_DIR/tunnel.pid"
URL=""
for _ in $(seq 1 40); do
  URL="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$HOME_DIR/tunnel.log" | head -1 || true)"
  [ -n "$URL" ] && break; sleep 1
done
[ -n "$URL" ] || { echo "No tunnel URL after 40 s; see $HOME_DIR/tunnel.log"; exit 1; }
HOST="${URL#https://}"
# 2. start the wrapper, allowing only that hostname
MCP_TRANSPORT=streamable-http MCP_PORT=3001 MCP_SECRET="$SECRET" MCP_ALLOWED_HOSTS="$HOST" nohup "$HOME_DIR/.venv/bin/python" "$HOME_DIR/server.py" > "$HOME_DIR/wrapper.log" 2>&1 &
echo $! > "$HOME_DIR/wrapper.pid"
sleep 4
echo
echo "Add this as a custom connector in claude.ai (Settings > Connectors), named exactly:  cube"
echo "URL:  $URL/$SECRET/mcp"
echo
echo "It stays up only while this laptop is awake and these processes run. The address changes if the tunnel restarts."
echo "Stop with: $HOME_DIR/stop_public_tunnel.sh"

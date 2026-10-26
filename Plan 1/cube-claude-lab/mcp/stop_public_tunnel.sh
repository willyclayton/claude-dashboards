#!/usr/bin/env bash
# Stop the public tunnel and the wrapper started by start_public_tunnel.sh.
HOME_DIR="$HOME/.cube-mcp"
for f in tunnel wrapper; do
  [ -f "$HOME_DIR/$f.pid" ] && kill "$(cat "$HOME_DIR/$f.pid")" 2>/dev/null && echo "stopped $f" || true
  rm -f "$HOME_DIR/$f.pid"
done
pkill -f "cloudflared tunnel --no-autoupdate" 2>/dev/null || true

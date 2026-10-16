#!/usr/bin/env bash
# Launch the TradingAgents Vue web UI (tradingagents-webui 0.1.0) on localhost only.
# The LLM key comes from Keychain (Fuel iX), never from .env; provider, backend URL
# and models come from TRADINGAGENTS_* in .env.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${PORT:-1100}"
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT is already in use. The web UI may already be running: http://127.0.0.1:$PORT"
  echo "Stop it with: kill \$(lsof -t -iTCP:$PORT -sTCP:LISTEN)   or pick another port: PORT=1101 \"$0\""
  exit 1
fi

OPENAI_API_KEY="$(security find-generic-password -s fuelix-api-key -a "$USER" -w 2>/dev/null)" || {
  echo "Fuel iX key not found in Keychain (service fuelix-api-key). Run: fuelix-set" >&2
  exit 1
}
export OPENAI_API_KEY
export TRADINGAGENTS_ROOT="$PWD"

# Bind 127.0.0.1, not the package default 0.0.0.0: the app ships CORS "*" and no auth.
exec uv run --with tradingagents-webui==0.1.0 \
  uvicorn tradingagents_webui.server:app --host 127.0.0.1 --port "$PORT"

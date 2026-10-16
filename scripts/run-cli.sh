#!/usr/bin/env bash
# Run the upstream TradingAgents CLI with the Fuel iX key from Keychain (never from .env).
# Provider, backend URL and models come from TRADINGAGENTS_* in .env, so those prompts are skipped.
# Pass any CLI flags through, e.g.: scripts/run-cli.sh --ticker NVDA --date 2026-10-14
set -euo pipefail
cd "$(dirname "$0")/.."

OPENAI_API_KEY="$(security find-generic-password -s fuelix-api-key -a "$USER" -w 2>/dev/null)" || {
  echo "Fuel iX key not found in Keychain (service fuelix-api-key). Run: fuelix-set" >&2
  exit 1
}
export OPENAI_API_KEY

exec uv run tradingagents "$@"

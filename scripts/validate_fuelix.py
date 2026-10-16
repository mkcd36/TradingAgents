"""Validate Fuel iX wiring for TradingAgents.

Checks, in order:
  1. tradingagents package import auto-loaded .env (OPENAI_API_KEY, backend URL).
  2. DEFAULT_CONFIG picked up the TRADINGAGENTS_LLM_BACKEND_URL override.
  3. langchain-openai (the same client TradingAgents uses) can hit Fuel iX
     and complete a chat round-trip with the configured deep + quick models.

Run from project root:
    uv run python scripts/validate_fuelix.py
"""

from __future__ import annotations

import os
import sys

import tradingagents  # noqa: F401  (triggers .env auto-load)
from tradingagents.default_config import DEFAULT_CONFIG


def fail(msg: str) -> None:
    print(f"FAIL  {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"OK    {msg}")


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY") or ""
    if not api_key:
        fail("OPENAI_API_KEY is empty after .env load.")
    ok(f"OPENAI_API_KEY loaded (len={len(api_key)}, prefix={api_key[:3]}...)")

    backend_url = DEFAULT_CONFIG.get("backend_url")
    expected = "https://api.fuelix.ai/v1"
    if backend_url != expected:
        fail(f"backend_url is {backend_url!r}; expected {expected!r}")
    ok(f"backend_url -> {backend_url}")

    provider = DEFAULT_CONFIG.get("llm_provider")
    if provider != "openai":
        fail(f"llm_provider is {provider!r}; expected 'openai'")
    ok(f"llm_provider -> {provider}")

    deep = DEFAULT_CONFIG.get("deep_think_llm")
    quick = DEFAULT_CONFIG.get("quick_think_llm")
    ok(f"deep_think_llm -> {deep}")
    ok(f"quick_think_llm -> {quick}")

    from langchain_openai import ChatOpenAI

    for label, model in (("quick", quick), ("deep", deep)):
        print(f"\n--- {label} model round-trip ({model}) ---")
        llm = ChatOpenAI(model=model, base_url=backend_url, api_key=api_key)
        resp = llm.invoke(f"Reply with exactly the token TA_{label.upper()}_OK and nothing else.")
        content = (resp.content or "").strip()
        if f"TA_{label.upper()}_OK" not in content:
            fail(f"{label} model did not return expected token. Got: {content!r}")
        ok(f"{label} ({model}) responded: {content}")

    print("\nAll checks passed. Fuel iX is wired into TradingAgents end-to-end.")


if __name__ == "__main__":
    main()

---
mode: LEAN
audience: SELF
classification:
  work_or_personal: PERSONAL
  personal_stakes: "NO"
  classified_at: 2026-10-15
---

# TradingAgents (personal fork)

Personal fork of [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents), a multi-agent LLM framework for financial trading analysis. Here it runs locally through the upstream CLI (the main interface) or a light Vue web UI, with the LLM calls going through Fuel iX.

| | |
|---|---|
| Fork (`origin`) | `https://github.com/mkcd36/TradingAgents` (account `mkcd36`) |
| Upstream | `https://github.com/TauricResearch/TradingAgents` |
| Working branch | `sync/upstream-0.6.0`: upstream v0.6.0 plus this scaffold and `scripts/run-webui.sh` / `scripts/validate_fuelix.py` |
| Old `main` | May 2026 fork, 292 commits behind; it holds the `--non-interactive` CLI flag (not ported) |

## Tech Stack

- **Language:** Python 3.12 (upstream requires ≥3.11), managed with `uv`
- **Framework:** upstream `tradingagents` package (LangGraph agents) plus `cli/`
- **Web UI:** [`tradingagents-webui==0.1.0`](https://pypi.org/project/tradingagents-webui/) (FastAPI + Vue 3 CDN + Tailwind). It is **not** a project dependency: it is overlaid at launch with `uv run --with`, so `uv sync` never removes it and upstream's `pyproject.toml` stays untouched.
- **Tests:** upstream pytest suite (`uv run pytest -q`)

## Run it

**Primary: the upstream CLI.** It's the maintained interface: live agent progress, every option, and a `complete_report.html` per run.

```bash
scripts/run-cli.sh                                  # interactive
scripts/run-cli.sh --ticker NVDA --date 2026-10-14  # skips those prompts
scripts/run-webui.sh        # secondary: quick browser UI at http://127.0.0.1:1100
uv run python scripts/validate_fuelix.py   # needs OPENAI_API_KEY exported (the launchers do this)
```

Both launchers export the Fuel iX key from Keychain. Plain `uv run tradingagents` fails, because `.env` no longer holds a key.

## Architectural Invariants

- **LLM = Fuel iX over the OpenAI-compatible provider.** In `.env`: `TRADINGAGENTS_LLM_PROVIDER=openai`, `TRADINGAGENTS_LLM_BACKEND_URL=https://api.fuelix.ai/v1`, and the models `gpt-5.4` (deep) and `gpt-5.4-mini` (quick). Fuel iX also serves Claude models on that endpoint, but the web UI's model dropdown is hard-coded to the OpenAI list.
- **The key is read from Keychain at launch, never from `.env`.** `scripts/run-webui.sh` exports `OPENAI_API_KEY` from Keychain `fuelix-api-key`. A stale May key in `.env` was removed on 2026-10-15. Upstream's `load_dotenv` does not override variables that are already set, so the launcher's value wins.
- **The web UI binds to localhost only.** The package defaults to `0.0.0.0` with CORS `*` and no auth, so anyone on the network could run analyses on your key or delete reports. Always launch through the script, which binds `127.0.0.1`.
- **Stay close to upstream.** Changes to this fork are additive files only (scripts, docs). Upstream code is not edited in place, so `git rebase upstream/main` stays cheap. The May reformat commit is why the old `main` could not be rebased.

## Web UI known limits (package 0.1.0)

- The agent progress panel is cosmetic: every status flips at once after `propagate()` returns.
- The date picker can default to tomorrow (UTC vs local time). Pick a past trading day.
- Deep and quick models are set to the same dropdown model, and analyst selection and research depth are not exposed. Use the CLI (`uv run tradingagents`) for full control.
- Reports go to `~/.tradingagents/reports/`, and the memory log is `~/.tradingagents/memory/trading_memory.md`.

## Conventions

- **Python toolchain = `uv` + `ruff`.** Never use system `python3` or `pytest`.
- **Sync upstream:** `git fetch upstream && git rebase upstream/main` on the working branch.
- **Commit messages:** imperative mood, scoped (`<area>: <change>`).
- **Never commit:** `.env`, API keys, generated reports.
- **Secrets:** API keys live in the 1Password personal `Programs` vault. Read Keychain coordinates from `~/My Projects/_program/secrets/secrets.yml`; the full spec is at `~/My Projects/_program/secrets/SPEC.md`. Never add credential VALUES to `.env`; use the Keychain entry registered in the spec.
- **Artifacts:** `docs/` holds canonical docs, `outputs/` dated deliverables, `archive/` superseded files. `docs/ARTIFACTS.md` is regenerated at every wrap.

## Not financial advice

This is research tooling. Its BUY/HOLD/SELL output is model-generated and does not place trades.

## Session Continuity

Trigger `"wrap up"` or `"log this session"` at session end. It appends a **Lean Wrap** to `docs/SESSION-LOG.md`.

## Mode promotion

Run `mode-router` to re-evaluate. Promote to ENTERPRISE if this ever executes trades, touches a brokerage account, or serves other users.

# PM Research Workflow

A lightweight 5-agent, depth-first stock research workflow for Codex-style execution.

## What it does

- Defines a 5-agent PM-oriented prompt stack:
  1. Fact Pack Agent
  2. Business Structure Agent
  3. Market Expectations Agent
  4. Variant View Agent
  5. PM Decision Agent
- Includes recommended rerun rules between agents.
- Generates per-ticker run folders with:
  - workflow instructions
  - agent prompts
  - per-agent task files
  - a run manifest
- Supports dry-run workflow generation without an API key.

## Quick start

```bash
python3 scripts/pm_workflow.py --tickers AAPL NVDA --analysis-date 2026-03-18 --investor-profile profiles/fund_manager.md --output-dir runs
```

## Output layout

Each ticker gets its own directory under `runs/`, with all prompts and task files isolated from other tickers.

"""
Tracks real OpenAI API spend across the generator pipeline and appends it
to COSTS.md. Before this, COSTS.md read a flat, unconditionally wrong
"$0.00 total spent" for months (found 2026-09-21) despite real per-unit
generation spend -- nothing was ever wired up to log it. Every generator
file's own ensure_openai_client() now routes its client through
wrap_client() here, so every chat.completions.create call anywhere in the
pipeline is logged automatically, with no per-call-site changes needed.

Logging failures must never break content generation -- log_cost() and
wrap_client()'s inner call both swallow errors rather than raise.
"""
from __future__ import annotations

import functools
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

COSTS_PATH = Path(__file__).parent.parent / "COSTS.md"

# USD per 1M tokens (input, output). Source: platform.openai.com/pricing
# at the time this was written -- a point-in-time snapshot, not fetched
# live, so treat as approximate and re-check periodically.
MODEL_RATES: dict[str, tuple[float, float]] = {
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1-nano": (0.10, 0.40),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
}
# Fallback matches the pipeline's actual default model (ai_lesson_engine.py,
# assessment_generator.py both default to "gpt-4.1-mini").
DEFAULT_RATE = MODEL_RATES["gpt-4.1-mini"]

_HEADER = (
    "# FocusLab Digital — Cost Tracker\n\n"
    "Auto-logged by cmie/cost_tracker.py from real OpenAI API usage "
    "(prompt/completion tokens x the rate table in that file). Rates are "
    "a point-in-time snapshot, not fetched live -- treat totals as "
    "approximate.\n\n"
    "| Date | Item | Amount (USD) | Notes |\n"
    "|------|------|-------------|-------|\n"
)


def _rate_for(model: str) -> tuple[float, float]:
    for key, rate in MODEL_RATES.items():
        if model.startswith(key):
            return rate
    return DEFAULT_RATE


def log_cost(usage: Any, model: str, context: str = "") -> float:
    """Append one row to COSTS.md for a single completed API call.
    Returns the computed USD cost (0.0 on any failure -- never raises)."""
    try:
        in_rate, out_rate = _rate_for(model)
        prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
        completion_tokens = getattr(usage, "completion_tokens", 0) or 0
        cost = (prompt_tokens / 1_000_000 * in_rate) + (completion_tokens / 1_000_000 * out_rate)

        if not COSTS_PATH.exists():
            COSTS_PATH.write_text(_HEADER, encoding="utf-8")

        text = COSTS_PATH.read_text(encoding="utf-8")
        lines = [l for l in text.splitlines() if not l.startswith("**Total spent")]
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        row = (
            f"| {date} | {context or model} | {cost:.4f} | "
            f"model={model}, prompt_tokens={prompt_tokens}, completion_tokens={completion_tokens} |"
        )
        lines.append(row)

        total = 0.0
        for l in lines:
            if l.startswith("|") and not l.startswith("| Date") and not l.startswith("|------"):
                parts = [p.strip() for p in l.split("|")]
                if len(parts) >= 4:
                    try:
                        total += float(parts[3])
                    except ValueError:
                        pass
        lines.append("")
        lines.append(f"**Total spent: ${total:.4f} USD** (OpenAI API only; auto-logged, approximate -- see header)")

        COSTS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return cost
    except Exception:
        return 0.0


def wrap_client(client: Any, context: str = "") -> Any:
    """Wrap an OpenAI client so every chat.completions.create call on it
    logs its real cost automatically. Call once from each module's
    ensure_openai_client(); every call site in that module benefits with
    no further changes."""
    original_create = client.chat.completions.create

    @functools.wraps(original_create)
    def traced_create(*args: Any, **kwargs: Any) -> Any:
        resp = original_create(*args, **kwargs)
        try:
            model = kwargs.get("model") or (args[0] if args else "unknown")
            usage = getattr(resp, "usage", None)
            if usage is not None:
                log_cost(usage, model=model, context=context)
        except Exception:
            pass
        return resp

    client.chat.completions.create = traced_create
    return client

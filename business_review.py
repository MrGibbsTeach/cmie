"""
business_review.py — a single recurring snapshot of the business: revenue
across all 3 platforms, catalog size, recent shipping activity, and a
maintained list of open decisions/follow-ups. Meant to be the one script
worth running weekly (or hooking to a real schedule via Claude Code cloud
scheduled tasks) instead of re-deriving this by hand each time.

Usage:
    python business_review.py              # print, don't save
    python business_review.py --save       # print + write BUSINESS_REVIEW.md
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()

from check_revenue import check_tpt, check_gumroad, check_tes

PROJECT_ROOT = Path(__file__).parent
OUT_MD = PROJECT_ROOT / "BUSINESS_REVIEW.md"

# Maintained by hand -- update as items get resolved or new ones surface.
# This is deliberately NOT auto-derived; open decisions belong to a human,
# not a heuristic.
OPEN_ITEMS = [
    "TES Unit 1 (AI series) still has the presenter-placeholder / 'Unknown' "
    "quote cosmetic bug -- TPT side fixed 2026-07-19, TES side not attempted "
    "yet (unfamiliar edit flow, real risk of repeating the Networks & "
    "Hardware licence-corruption mistake without live oversight).",
    "TES has a genuine duplicate: 'Data Shapes the AI World – Lesson 1' "
    "exists as two separate resources (13432831, 13432796). Needs explicit "
    "delete authorization -- not actioned autonomously.",
    "TES resource 13445828 is permanently broken (TES's own 'temporary "
    "disruption' error on every step, confirmed non-transient). Likely "
    "dead/orphaned; candidate for deletion, needs authorization.",
    "Off-brand Gumroad products (A$129 SWMS, ADHD guide) still share the "
    "teaching storefront -- undecided, business-judgment call.",
    "Shelved AI-series Units 3-8 are deactivated on TPT (2026-07-19) but "
    "still live on TES (9 resources, Unit 1 only per the 2026-07-18 audit) "
    "-- Unit 1's content itself was confirmed clean, no action needed there.",
    "No real unattended scheduling exists yet -- Claude Code cloud "
    "scheduled tasks (claude.ai/code/scheduled) would need setup via the "
    "web UI; this script is designed to be the payload for that once set up.",
]


def _git_recent(n: int = 8) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "log", f"-{n}", "--pretty=%ad %s", "--date=short"],
            capture_output=True, text=True, timeout=15,
        )
        return [l for l in out.stdout.splitlines() if l.strip()]
    except Exception as e:
        return [f"(could not read git log: {e})"]


def _catalog_units() -> list[str]:
    units_dir = PROJECT_ROOT / "releases" / "public"
    if not units_dir.exists():
        return []
    seen = set()
    for p in sorted(units_dir.glob("*_v001")):
        name = p.name.replace("_v001", "")
        if "ai_data" not in name:
            seen.add(name)
    return sorted(seen)


def build_report(headless: bool = True) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Business Review — {now}", ""]

    lines.append("## Revenue")
    total_notes = []
    for label, fn, earnings_key in [
        ("TPT", check_tpt, "total_earnings"),
        ("Gumroad", check_gumroad, "total_revenue"),
        ("TES", check_tes, "total_earnings"),
    ]:
        try:
            r = fn(headless)
            if r.get("error"):
                lines.append(f"- **{label}**: ERROR — {r['error']}")
                continue
            earnings = r.get(earnings_key, 0)
            sales = r.get("sales_count", 0)
            currency = r.get("currency", "")
            lines.append(f"- **{label}**: {currency} {earnings} net, {sales} sale(s)")
            total_notes.append(f"{currency}{earnings}")
        except Exception as e:
            lines.append(f"- **{label}**: ERROR — {e}")
    lines.append(f"- **Combined (not currency-converted)**: {' + '.join(total_notes)}")
    lines.append("")

    units = _catalog_units()
    lines.append(f"## Catalog — {len(units)} live unit(s)")
    for u in units:
        lines.append(f"- {u}")
    lines.append("")

    lines.append("## Recent activity (last 8 commits)")
    for l in _git_recent(8):
        lines.append(f"- {l}")
    lines.append("")

    lines.append("## Open items / decisions waiting on you")
    for item in OPEN_ITEMS:
        lines.append(f"- {item}")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save", action="store_true", help="Also write BUSINESS_REVIEW.md")
    parser.add_argument("--headless", action="store_true", default=True)
    args = parser.parse_args()

    report = build_report(headless=args.headless)
    print(report)

    if args.save:
        OUT_MD.write_text(report, encoding="utf-8")
        print(f"\nSaved to {OUT_MD}")


if __name__ == "__main__":
    main()

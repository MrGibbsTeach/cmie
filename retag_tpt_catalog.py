"""
retag_tpt_catalog.py -- bring every live CMIE TPT product in line with the
2026-09-26 market-positioning decisions, in ONE edit per product:

  1. Grade boxes: tick 6th, 7th, 8th (never untick anything, never add 9th).
  2. Tick "Appropriate for Australia".
  3. Append one audience line to the description (Grades 6-8 / Year 7 /
     KS3 / ages 11-14 / ACARA) so no market is lost -- TPT's tag list is a
     closed taxonomy with no entry for any of those terms (verified live),
     so the description is the only place they can go.
  4. Title: drop the single-year label ("Year 7", "Lower Secondary"), keep
     the specific lesson/topic keywords first, and end with "Grades 6-8"
     where it fits in TPT's 80-char limit. Lead magnets (free products) and
     the flagship keep their titles.

Every save is verified by reloading the edit page and reading the values
back (the old title fix reported ~90 false successes by trusting the
absence of an error -- see edit_product_title in cmie/publishing/tpt.py for
the real cause: the edit form's "Upload thumbnails later" default makes
TPT's submit handler silently do nothing).

Usage:
    python retag_tpt_catalog.py --dry-run            # read-only, prints plan
    python retag_tpt_catalog.py --ids 16835617       # real edit, one product
    python retag_tpt_catalog.py                      # everything not yet done
Results are appended to data/tpt_retag_log.json; finished ids are skipped on
re-run so an interrupted run resumes.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
LOG_PATH = PROJECT_ROOT / "data" / "tpt_retag_log.json"
UNITS_GLOB = str(PROJECT_ROOT / "data" / "units" / "year7_*_unit1.json")

# Every CMIE product is id >= this; below it is the shelved AI series and
# legacy non-CMIE products, which this script must never touch.
MIN_CMIE_ID = 16818000

GRADE_SUFFIX = "Grades 6-8"
AUDIENCE_LINE = (
    "Grade levels: Grades 6-8 (US Middle School) | Year 7 (Australia, ACARA v9 "
    "Digital Technologies) | KS3 (England) | Ages 11-14."
)
AUDIENCE_MARKER = "KS3 (England)"
GRADES_TO_TICK = ["6th-grade", "7th-grade", "8th-grade"]
DASH = "–"


# ---------------------------------------------------------------------------
# Unit metadata (from the unit configs, so titles never depend on guesswork)
# ---------------------------------------------------------------------------

def load_units() -> list[dict]:
    units = []
    for f in sorted(glob.glob(UNITS_GLOB)):
        c = json.loads(Path(f).read_text(encoding="utf-8"))
        title = c["title"]
        if ":" in title:
            topic, rest = title.split(":", 1)
            subtitle = rest.split(DASH, 1)[-1].strip()
        else:
            topic = title.split(" Unit ")[0]
            subtitle = title.split(DASH, 1)[-1].strip()
        units.append({"unit_id": c["unit_id"], "topic": topic.strip(), "subtitle": subtitle, "title": title})
    return units


def match_unit(units: list[dict], desc_first: str, live_title: str) -> dict | None:
    """Find the unit a product belongs to, refusing anything ambiguous.

    Tiers, first tier with exactly ONE hit wins: (1) full subtitle in the
    description's first line (never truncated by TPT's 80-char title cap),
    (2) full subtitle in the live title, (3) topic name in either. No
    prefix matching: a 22-char subtitle prefix once matched the Web Design
    lesson "Designing and Building a Website" to Game Design ("Designing
    and Building Your First Game")."""
    def norm(x: str) -> str:
        return x.lower().replace("–", "-").replace("�", "-")

    live = [u for u in units if u["unit_id"] != "year7_ai_data_unit1"]
    d, t = norm(desc_first), norm(live_title)
    tiers = [
        [u for u in live if norm(u["subtitle"]) in d],
        [u for u in live if norm(u["subtitle"]) in t],
        [u for u in live if norm(u["topic"]) in d or norm(u["topic"]) in t],
    ]
    for hits in tiers:
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            return None
    return None


# ---------------------------------------------------------------------------
# Title rules
# ---------------------------------------------------------------------------

def _fits(s: str) -> bool:
    return len(s) <= 80


def first_that_fits(candidates: list[str]) -> str | None:
    for c in candidates:
        if _fits(c):
            return c
    return None


# Complete "(Year 7 / Grade 7 ...)" / "(Lower Secondary)" suffix, or the same
# suffix cut off mid-way by TPT's 80-char title limit (no closing bracket).
YEAR_PAREN = re.compile(
    r"\s*\((?:[^()]*\b(?:Year|Yr)\s*7\b[^()]*|Lower Secondary)\)\s*|\s*\((?:Year|Yr|Lower)[^)]*$",
    re.I,
)


def classify(live_title: str, desc_first: str, free: bool) -> str:
    t = live_title
    if free:
        return "leadmagnet"
    if "Complete Digital Technologies Curriculum" in t:
        return "flagship"
    if "2-Unit" in t and "Bundle" in t:
        return "bundle2"
    if "Assessment Pack" in t or "Assessment Pack" in desc_first:
        return "assessment"
    if "|" in t and not YEAR_PAREN.search(t):
        return "lesson"
    if YEAR_PAREN.search(t) or re.search(rf"Unit \d\s*[{DASH}-]", t):
        return "unit"
    return "unknown"


def new_title(units: list[dict], live_title: str, desc_first: str, free: bool) -> tuple[str, str, str]:
    """Returns (kind, new_title, note). new_title == live_title means leave
    unchanged (note says why)."""
    kind = classify(live_title, desc_first, free)
    if kind in ("leadmagnet", "flagship"):
        return kind, live_title, f"{kind}: title kept"

    if kind == "bundle2":
        old_fmt = re.match(rf"^(.+?)\s+Bundle\s*[{DASH}-]\s*2-Unit", live_title)
        if old_fmt:  # "<Name> Bundle - 2-Unit Digital Technologies Bundle (14 Lessons..."
            base = f"{old_fmt.group(1).strip()} | 2-Unit Bundle, 14 Lessons"
        else:
            base = YEAR_PAREN.sub(" ", live_title).replace("  ", " ").strip()
            base = re.sub(rf"\s*\|\s*{GRADE_SUFFIX}\s*$", "", base)
        cand = first_that_fits([f"{base} | {GRADE_SUFFIX}", base])
        return kind, cand or live_title, "" if cand else "too long, kept"

    unit = match_unit(units, desc_first, live_title)
    if unit is None:
        return kind, live_title, "no unit match, title kept"
    topic = unit["topic"]

    if kind == "assessment":
        cand = first_that_fits([f"{topic} | Assessment Pack | {GRADE_SUFFIX}", f"{topic} | Assessment Pack"])
        return kind, cand or live_title, "" if cand else "too long, kept"

    if kind == "unit":
        base = YEAR_PAREN.sub(" ", live_title).replace("  ", " ").strip()
        short = re.sub(rf"Unit \d\s*{DASH}\s*", "", base)
        cand = first_that_fits([f"{base} | {GRADE_SUFFIX}", f"{short} | {GRADE_SUFFIX}", base, short])
        return kind, cand or live_title, "" if cand else "too long, kept"

    if kind == "lesson":
        lesson = live_title.split("|")[0].strip()
        m = re.search(r"Lesson\s+(\d+)", desc_first) or re.search(r"Lesson\s+(\d+)", live_title)
        if not m:
            return kind, live_title, "lesson number not found, title kept"
        n = m.group(1)
        if lesson.lower().startswith(unit["topic"].lower()) or lesson.lower().startswith("unit "):
            return kind, live_title, "first segment is not a lesson title, kept"
        cand = first_that_fits([
            f"{lesson} | {topic} | Lesson {n} | {GRADE_SUFFIX}",
            f"{lesson} | {topic} | Lesson {n}",
            f"{lesson} | Lesson {n} | {GRADE_SUFFIX}",
            f"{lesson} | Lesson {n}",
        ])
        return kind, cand or live_title, "" if cand else "too long, kept"

    return kind, live_title, "unknown kind, title kept"


# ---------------------------------------------------------------------------
# Browser side
# ---------------------------------------------------------------------------

READ_STATE_JS = """() => {
  const q = (s) => document.querySelector(s);
  const title = (q('input[name="data[Item][name]"]') || {}).value || '';
  const freeBtn = q('label[for="item-free"] button[role="checkbox"]');
  const ed = q('[contenteditable="true"]');
  const desc = ed ? ed.innerText : '';
  const grades = {};
  document.querySelectorAll('button[role="checkbox"]').forEach(b => {
    const n = b.getAttribute('name') || b.id || '';
    if (n.startsWith('data.Grade.Grade-checkbox_')) grades[n.replace('data.Grade.Grade-checkbox_', '')] = b.getAttribute('aria-checked') === 'true';
  });
  let au = null;
  document.querySelectorAll('label').forEach(l => {
    if (/Appropriate for Australia/i.test(l.innerText)) { const b = l.querySelector('button[role="checkbox"]'); if (b) au = b.getAttribute('aria-checked') === 'true'; }
  });
  return {title, free: freeBtn ? freeBtn.getAttribute('aria-checked') === 'true' : false, desc, grades, au};
}"""


def enumerate_products(page) -> dict[str, str]:
    from cmie.publishing.tpt import DASHBOARD_URL
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4000)
    found: dict[str, str] = {}
    n = 1
    while True:
        for a in page.evaluate(
            """() => Array.from(document.querySelectorAll("a[href*='/Product/']")).map(a => ({t:(a.textContent||'').trim(), h:a.href})).filter(x => x.t)"""
        ):
            found[a["h"]] = a["t"]
        nxt = page.locator(f'a[aria-label="Go to page {n + 1}"]')
        if nxt.count() == 0:
            break
        page.wait_for_timeout(1500)
        nxt.first.click(force=True)
        page.wait_for_timeout(3500)
        n += 1
    return found


def product_id(url: str) -> str | None:
    m = re.search(r"-(\d+)/?$", url.rstrip("/"))
    return m.group(1) if m else None


def read_state(page, pid: str) -> dict:
    page.goto(f"https://www.teacherspayteachers.com/itemsDigital/editNext/{pid}", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4500)
    # The React description editor pops in late on some products; an early
    # read sees an empty description (found 2026-09-26, product 17046914).
    # A few listings (e.g. 17046914) have NO description section on the edit
    # form at all; those get everything except the description line.
    has_editor = True
    try:
        page.wait_for_selector('[contenteditable="true"]', timeout=25000)
    except Exception:
        has_editor = False
    page.wait_for_timeout(800)
    st = page.evaluate(READ_STATE_JS)
    st["has_editor"] = has_editor
    return st


def plan_for(units: list[dict], st: dict) -> dict:
    desc_first = (st["desc"].split("\n")[0] if st["desc"] else "").strip()
    kind, title, note = new_title(units, st["title"], desc_first, st["free"])
    ticked = [g for g, v in st["grades"].items() if v]
    to_tick = [g for g in GRADES_TO_TICK if not st["grades"].get(g)]
    over_limit = len(ticked) + len(to_tick) > 4
    return {
        "kind": kind,
        "old_title": st["title"],
        "new_title": title,
        "title_note": note,
        "grades_to_tick": [] if over_limit else to_tick,
        "grades_note": f"would exceed 4 grades ({ticked})" if over_limit else "",
        "tick_au": st["au"] is False,
        "append_desc": st["has_editor"] and AUDIENCE_MARKER not in st["desc"],
    }


def apply_and_verify(page, pid: str, plan: dict) -> str:
    """Applies the plan on the ALREADY-LOADED edit page, saves, reloads and
    verifies. Returns "OK" or raises RuntimeError."""
    if plan["new_title"] != plan["old_title"]:
        page.locator('input[name="data[Item][name]"]').first.fill(plan["new_title"])

    for g in plan["grades_to_tick"]:
        gid = f"data.Grade.Grade-checkbox_{g}"
        page.locator(f'button[role="checkbox"][id="{gid}"], button[role="checkbox"][name="{gid}"]').first.click()
        page.wait_for_timeout(250)

    if plan["tick_au"]:
        page.locator('label:has-text("Appropriate for Australia") button[role="checkbox"]').first.click()
        page.wait_for_timeout(250)

    if plan["append_desc"]:
        ed = page.locator('[contenteditable="true"]').first
        ed.click()
        page.keyboard.press("Control+End")
        page.keyboard.press("Enter")
        page.keyboard.type(AUDIENCE_LINE, delay=0)
        page.wait_for_timeout(500)

    # See edit_product_title() for why this radio must be selected.
    page.get_by_text("Upload thumbnails now", exact=False).first.click()
    page.wait_for_timeout(800)
    submit = page.locator("#react-submit-section button[type='submit']").first
    submit.scroll_into_view_if_needed(timeout=10000)
    submit.click()
    try:
        page.wait_for_url(re.compile(r"/Product/"), timeout=60000)
    except Exception:
        err = page.locator("text=/^Please (select|upload|enter|fix|choose|include|add|provide)/i")
        raise RuntimeError("save did not redirect: " + (err.first.inner_text()[:160] if err.count() else "no visible error"))

    st = read_state(page, pid)
    problems = []
    if st["title"].strip() != plan["new_title"].strip():
        problems.append(f"title stored {st['title']!r}")
    for g in GRADES_TO_TICK:
        if g not in plan["grades_to_tick"] and not st["grades"].get(g):
            if plan["grades_note"]:
                continue
        if g in plan["grades_to_tick"] and not st["grades"].get(g):
            problems.append(f"grade {g} not saved")
    if plan["tick_au"] and not st["au"]:
        problems.append("Australia box not saved")
    if plan["append_desc"] and AUDIENCE_MARKER not in st["desc"]:
        problems.append("description line not saved")
    if problems:
        raise RuntimeError("; ".join(problems))
    return "OK"


def load_log() -> dict:
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    return {}


def save_log(log: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Read every product and print the plan; change nothing")
    ap.add_argument("--ids", help="Comma-separated product ids to process (default: all CMIE products)")
    ap.add_argument("--limit", type=int, help="Process at most N products")
    args = ap.parse_args()

    from cmie.publishing.browser import automation_chrome
    from cmie.publishing.tpt import _login

    units = load_units()
    log = load_log()

    with automation_chrome() as (ctx, page):
        _login(page, ctx, os.environ.get("TPT_EMAIL", ""), os.environ.get("TPT_PASSWORD", ""))
        if args.ids:
            ids = [i.strip() for i in args.ids.split(",")]
        else:
            listing = enumerate_products(page)
            ids = sorted({product_id(h) for h in listing if product_id(h) and int(product_id(h)) >= MIN_CMIE_ID})
        if not args.dry_run:
            ids = [i for i in ids if log.get(i, {}).get("status") != "OK"]
        if args.limit:
            ids = ids[: args.limit]
        print(f"{len(ids)} product(s) to process (dry_run={args.dry_run})", flush=True)

        counts = {"OK": 0, "ERROR": 0, "PLANNED": 0}
        for pid in ids:
            try:
                st = read_state(page, pid)
                plan = plan_for(units, st)
                if args.dry_run:
                    counts["PLANNED"] += 1
                    log_line = f"[{pid}] {plan['kind']:<10} grades+{plan['grades_to_tick']} AU={plan['tick_au']} desc+={plan['append_desc']}"
                    print(log_line, flush=True)
                    if plan["new_title"] != plan["old_title"]:
                        print(f"      OLD: {plan['old_title']}\n      NEW: {plan['new_title']}", flush=True)
                    if plan["title_note"] or plan["grades_note"]:
                        print(f"      NOTE: {plan['title_note']} {plan['grades_note']}", flush=True)
                    continue
                status = apply_and_verify(page, pid, plan)
                counts["OK"] += 1
                log[pid] = {"status": status, **plan}
                print(f"[{pid}] OK {plan['kind']}: {plan['new_title']}", flush=True)
            except Exception as e:
                counts["ERROR"] += 1
                log[pid] = {"status": "ERROR", "error": str(e)[:300]}
                print(f"[{pid}] ERROR {str(e)[:300]}", flush=True)
            if not args.dry_run:
                save_log(log)
            page.wait_for_timeout(1500)

    print("SUMMARY", counts, flush=True)


if __name__ == "__main__":
    main()

"""
produce_unit.py — One command from unit config to draft listings.

Chains the proven per-unit playbook (PROGRESS.md "Next Session" Priority 4):

    stage 1  pipeline   python -m cmie.pipeline.full_product_pipeline (OpenAI cost!)
    stage 2  qa         automated spot-checks (AI-leftover language, '- - ' bullets)
    stage 3  thumbnail  cmie/publishing/thumbnail.py::generate_thumbnail
    stage 4  package    package_unit.py (7 lesson zips + assessment + bundle + PUBLIC)
    ---------------- default STOP here ----------------
    stage 5  tpt        publish_tpt.py per part, WITHOUT --publish (drafts only)
    stage 6  gumroad    publish_gumroad.py (creates a DRAFT product)
    stage 7  tes        publish_tes.py (stops at draft, never clicks Publish now)

SAFETY: stages 5-7 never run unless --draft-publish is passed. Nothing in
this script can make a listing live — publish_tpt.py is always invoked
without --publish, and the Gumroad/TES scripts stop at draft by design.
After stages 5-7 you must still verify against the real dashboards
(fresh reload, not script output) and click publish manually.

Usage:
    python produce_unit.py --unit-config data/units/<id>.json
    python produce_unit.py --unit-config ... --from package        # resume
    python produce_unit.py --unit-config ... --only thumbnail
    python produce_unit.py --unit-config ... --skip pipeline
    python produce_unit.py --unit-config ... --draft-publish       # incl. stages 5-7
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Crash-proof console output on Windows cp1252 terminals.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).parent
RELEASES_ROOT = PROJECT_ROOT / "releases"

STAGES = ["pipeline", "qa", "thumbnail", "package", "tpt", "gumroad", "tes"]
PUBLISH_STAGES = {"tpt", "gumroad", "tes"}

# Proven-real TPT tag vocabulary (topic-specific terms don't exist in TPT's
# controlled vocabulary — discovered 2026-06-26).
DEFAULT_TPT_TAGS = (
    "Lessons, Activities, Career and Technical Education, "
    "Critical Thinking and Problem Solving"
)
TPT_PARTS = [f"lesson{n:02d}" for n in range(1, 8)] + ["assessment", "bundle"]

# Only ever surface these lines from publish subprocess output — a `tail`
# once truncated a success line and caused a double-publish (PROGRESS.md).
PUBLISH_LINE_FILTER = re.compile(r"Submitted|ERROR|WARNING|draft|Draft|FORM FILLED", re.I)


def _run(cmd: list[str], filter_output: bool = False) -> int:
    """Run a subprocess, streaming (optionally filtered) output."""
    print(f"\n$ {' '.join(str(c) for c in cmd)}")
    proc = subprocess.Popen(
        [str(c) for c in cmd],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    for line in proc.stdout:
        line = line.rstrip()
        if not filter_output or PUBLISH_LINE_FILTER.search(line):
            print(f"  {line}")
    proc.wait()
    return proc.returncode


def _state_path(unit_id: str) -> Path:
    return RELEASES_ROOT / unit_id / ".produce_state.json"


def _load_state(unit_id: str) -> dict:
    p = _state_path(unit_id)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"completed": []}


def _mark_done(unit_id: str, stage: str) -> None:
    state = _load_state(unit_id)
    if stage not in state["completed"]:
        state["completed"].append(stage)
    p = _state_path(unit_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------

def stage_pipeline(cfg: dict, cfg_path: Path, args) -> None:
    # GUARD: the pipeline stage calls OpenAI (costs money) and OVERWRITES
    # releases/<unit>/ + releases/public/<unit>_<version>/. If this unit has
    # already been packaged/shipped, regenerating must be an explicit choice
    # — a rerun silently diverges the local source folders from what
    # customers actually bought. (Added 2026-07-02 after exactly that
    # happened during testing.)
    unit_id = cfg["unit_id"]
    version = cfg.get("version", "v001")
    public_zip = RELEASES_ROOT / "artifacts" / f"{unit_id}_{version}_PUBLIC.zip"
    if public_zip.exists() and not args.allow_regenerate:
        raise RuntimeError(
            f"{public_zip.name} already exists — this unit looks already "
            f"packaged/shipped. Rerunning the pipeline would regenerate all "
            f"content (OpenAI cost) and overwrite the release folders. "
            f"Pass --allow-regenerate if you really mean to, or resume with "
            f"--from qa / --from package."
        )
    rc = _run([sys.executable, "-m", "cmie.pipeline.full_product_pipeline",
               "--unit-config", cfg_path])
    if rc != 0:
        raise RuntimeError(f"full_product_pipeline exited {rc}")


def stage_qa(cfg: dict, cfg_path: Path, args) -> None:
    """Automated version of the playbook's manual spot-checks (step 3)."""
    unit_id = cfg["unit_id"]
    unit_root = RELEASES_ROOT / unit_id
    problems: list[str] = []

    # 1. AI-leftover language in customer-facing generated text (the AI
    #    series' hardcoded assumptions leaked into non-AI units before).
    ai_pat = re.compile(r"\bAI\b")
    for md in list(unit_root.rglob("*.md")):
        if "listings" not in md.parts and md.parent.name not in (
            "assessment", "workbook", "roadmap", "readme"
        ) and md.name != "validation_report.md":
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if ai_pat.search(line):
                problems.append(f"AI-leftover language: {md.relative_to(unit_root)}:{i}: {line.strip()[:90]}")

    # 2. Flattened nested bullets ('- - text') in generated markdown.
    for md in unit_root.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if line.startswith("- - "):
                problems.append(f"Nested-bullet artifact: {md.relative_to(unit_root)}:{i}")

    if problems:
        print("\nQA FINDINGS (review before publishing — not hard failures if the topic legitimately mentions AI):")
        for p in problems[:40]:
            print(f"  ! {p}")
        if not args.ignore_qa:
            raise RuntimeError(
                f"{len(problems)} QA findings. Review them, then rerun with "
                f"--from thumbnail (or --ignore-qa if they're false positives)."
            )
    else:
        print("QA spot-checks passed: no AI-leftover language, no '- - ' artifacts.")


def stage_thumbnail(cfg: dict, cfg_path: Path, args) -> None:
    from cmie.publishing.thumbnail import generate_thumbnail
    out_dir = Path(args.thumbnail_dir) if args.thumbnail_dir else (RELEASES_ROOT / "thumbnails")
    out = generate_thumbnail(cfg["title"], cfg, out_dir)
    print(f"Thumbnail written: {out}")


def stage_package(cfg: dict, cfg_path: Path, args) -> None:
    from package_unit import package_unit
    package_unit(
        cfg["unit_id"],
        version=cfg.get("version", "v001"),
        out_dir=Path(args.package_out_dir) if args.package_out_dir else None,
        force=args.force_package,
    )


def stage_tpt(cfg: dict, cfg_path: Path, args) -> None:
    unit_id = cfg["unit_id"]
    for part in TPT_PARTS:
        rc = _run(
            [sys.executable, "publish_tpt.py", "--unit", unit_id,
             "--part", part, "--tags", args.tpt_tags],
            filter_output=True,  # never tail/truncate — see PROGRESS.md lesson
        )
        if rc != 0:
            raise RuntimeError(
                f"publish_tpt.py --part {part} exited {rc}. Verify on the real "
                f"My-Products page (fresh reload) before rerunning — a previous "
                f"false 'failure' caused a duplicate product."
            )
    print("\nTPT: all parts submitted WITHOUT --publish. Verify on My-Products, then publish manually.")


def stage_gumroad(cfg: dict, cfg_path: Path, args) -> None:
    rc = _run(
        [sys.executable, "publish_gumroad.py", "--unit", cfg["unit_id"],
         "--price", str(args.gumroad_price)],
        filter_output=True,
    )
    if rc != 0:
        raise RuntimeError("publish_gumroad.py failed — verify on the Gumroad dashboard (fresh reload).")
    print("\nGumroad: draft created. Verify zip size persisted after reload before publishing manually.")


def stage_tes(cfg: dict, cfg_path: Path, args) -> None:
    rc = _run(
        [sys.executable, "publish_tes.py", "--unit", cfg["unit_id"],
         "--price", str(args.tes_price)],
        filter_output=True,
    )
    if rc != 0:
        raise RuntimeError("publish_tes.py failed — verify on the TES Author Dashboard (fresh reload).")
    print("\nTES: draft saved. Review on Author Dashboard, check copyright box and publish manually.")


STAGE_FUNCS = {
    "pipeline": stage_pipeline,
    "qa": stage_qa,
    "thumbnail": stage_thumbnail,
    "package": stage_package,
    "tpt": stage_tpt,
    "gumroad": stage_gumroad,
    "tes": stage_tes,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Produce a unit end-to-end: pipeline -> qa -> thumbnail -> package (-> draft publish)."
    )
    parser.add_argument("--unit-config", required=True, help="data/units/<unit_id>.json")
    parser.add_argument("--from", dest="from_stage", choices=STAGES,
                        help="Resume from this stage (skips earlier ones)")
    parser.add_argument("--only", choices=STAGES, help="Run exactly one stage")
    parser.add_argument("--skip", default="", help="Comma-separated stages to skip")
    parser.add_argument("--draft-publish", action="store_true",
                        help="Also run the tpt/gumroad/tes DRAFT publish stages "
                             "(nothing is ever made live by this script)")
    parser.add_argument("--resume", action="store_true",
                        help="Skip stages already recorded as completed in releases/<unit>/.produce_state.json")
    parser.add_argument("--ignore-qa", action="store_true", help="Treat QA findings as warnings")
    parser.add_argument("--allow-regenerate", action="store_true",
                        help="Allow the pipeline stage to rerun for a unit whose "
                             "_PUBLIC.zip already exists (costs OpenAI money and "
                             "overwrites release folders)")
    parser.add_argument("--force-package", action="store_true",
                        help="Overwrite existing zips in releases/artifacts")
    parser.add_argument("--package-out-dir", help="Write zips somewhere other than releases/artifacts (testing)")
    parser.add_argument("--thumbnail-dir", help="Write thumbnail somewhere other than releases/thumbnails (testing)")
    parser.add_argument("--tpt-tags", default=DEFAULT_TPT_TAGS)
    parser.add_argument("--gumroad-price", default="12.99")
    parser.add_argument("--tes-price", default="9.99")
    args = parser.parse_args()

    cfg_path = Path(args.unit_config)
    if not cfg_path.exists():
        print(f"ERROR: unit config not found: {cfg_path}")
        sys.exit(1)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    unit_id = cfg["unit_id"]

    # Work out which stages run
    if args.only:
        stages = [args.only]
    else:
        stages = list(STAGES)
        if args.from_stage:
            stages = stages[stages.index(args.from_stage):]
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    state = _load_state(unit_id) if args.resume else {"completed": []}

    plan = []
    for s in stages:
        if s in skip:
            continue
        if s in state["completed"]:
            continue
        if s in PUBLISH_STAGES and not args.draft_publish:
            continue
        plan.append(s)

    print(f"Unit  : {unit_id}")
    print(f"Stages: {' -> '.join(plan) if plan else '(nothing to do)'}")
    if not args.draft_publish and not args.only:
        print("NOTE  : stopping before any publish stage. Pass --draft-publish to also")
        print("        create TPT/Gumroad/TES DRAFTS (still nothing goes live).")

    for stage in plan:
        print(f"\n{'=' * 66}\nSTAGE: {stage}\n{'=' * 66}")
        try:
            STAGE_FUNCS[stage](cfg, cfg_path, args)
        except Exception as e:
            print(f"\nSTAGE '{stage}' FAILED: {e}")
            print(f"Fix the issue, then resume with: python produce_unit.py "
                  f"--unit-config {cfg_path} --from {stage}"
                  + (" --draft-publish" if args.draft_publish else ""))
            sys.exit(1)
        _mark_done(unit_id, stage)

    print(f"\nAll requested stages complete for {unit_id}.")
    if args.draft_publish and any(s in PUBLISH_STAGES for s in plan):
        print("REMINDER: verify each platform's REAL dashboard with a fresh reload "
              "(poll 20-30s for persistence) before manually publishing anything.")


if __name__ == "__main__":
    main()

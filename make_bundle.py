"""
make_bundle.py — combine 2-3 already-published units' persisted zips into
one multi-unit bundle product, with a template-based (zero-OpenAI-cost)
listing description. No new content generation.

This is the missing piece behind RESOURCE_DROP_QUEUE.md's "Small bundle
packages" category: that category was written assuming a way to "combine
existing zips" already existed, but no such tool existed anywhere in this
repo (found 2026-09-04 -- see AUTONOMOUS_LOG.md). It also assumed each
unit's full content was available to combine, which wasn't true either
until package_unit.py started persisting each unit's _PUBLIC.zip to
data/units/packaged/ (git-tracked, survives across cloud containers,
unlike releases/).

Usage:
    python make_bundle.py --bundle-id programming_foundations_bundle \\
        --title "Programming Foundations Bundle" \\
        --units year7_algorithms_unit1 year7_python_programming_unit1 \\
        --price-aud 19.99 --price-gbp 14.99

Output (both files are byte-identical -- same convention package_unit.py
already uses for a single unit's _PUBLIC.zip vs _BUNDLE.zip):
    releases/artifacts/<bundle-id>_v001_PUBLIC.zip
    releases/artifacts/<bundle-id>_v001_BUNDLE.zip
        (each source unit's customer files under a <unit_id>/ subfolder,
        so lesson numbering/filenames from different units never collide)
    releases/<bundle-id>/listings/unit/{tpt,gumroad,tes}_listing.md
        (title/description in the exact format each publish script's own
        listing reader expects)
    data/units/marketing/<bundle-id>_listing.md
        (human-readable reference copy with prices noted -- not read by
        any publish script)

Treating <bundle-id> as a pseudo unit_id means the existing publish
scripts work completely unmodified: publish_gumroad.py and
publish_tes.py both resolve their zip by globbing
releases/artifacts/{unit_id}_*_PUBLIC.zip and their listing at
releases/{unit_id}/listings/unit/*_listing.md, and publish_tpt.py's
--part bundle looks for {unit_id}_v001_BUNDLE.zip -- so
`--unit <bundle-id>` on any of the three just works, no --zip or
copy-pasted listing text needed. Exception: TPT's price still comes from
the TPT_BUNDLE_PRICE env var (its markdown listing path has no price
field) -- override it for the bundle call, see the script's own printed
next-steps.

Requires each unit to already have data/units/packaged/<unit_id>_v001_PUBLIC.zip
(written automatically by package_unit.py's New Unit Production step for
every unit built from now on). If a unit predates that persistence step,
this refuses rather than silently building an incomplete bundle -- run
package_unit.py --unit <id> again first if its releases/ content still
exists in this container, or treat it as needing a one-time backfill.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
PACKAGED_ROOT = PROJECT_ROOT / "data" / "units" / "packaged"
UNITS_ROOT = PROJECT_ROOT / "data" / "units"
MARKETING_ROOT = UNITS_ROOT / "marketing"
ARTIFACTS_ROOT = PROJECT_ROOT / "releases" / "artifacts"


def _packaged_zip(unit_id: str, version: str) -> Path:
    return PACKAGED_ROOT / f"{unit_id}_{version}_PUBLIC.zip"


def _load_unit_config(unit_id: str) -> dict:
    path = UNITS_ROOT / f"{unit_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"No unit config at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_bundle_zip(bundle_id: str, unit_ids: list[str], version: str = "v001") -> Path:
    missing = [u for u in unit_ids if not _packaged_zip(u, version).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing persisted content for: " + ", ".join(missing) + "\n"
            f"Expected at {PACKAGED_ROOT}/<unit_id>_{version}_PUBLIC.zip for each.\n"
            "This unit predates package_unit.py's persistence step (added "
            "2026-09-05) or its packaged zip was never committed. Re-run "
            "package_unit.py --unit <id> in an environment where "
            "releases/public/<id>_<version>/ still exists, or treat this "
            "as needing a one-time backfill -- do not regenerate via the "
            "paid content pipeline just to unblock a bundle."
        )

    ARTIFACTS_ROOT.mkdir(parents=True, exist_ok=True)
    # Written under both names -- bundle_id doubles as a pseudo unit_id so
    # publish_gumroad.py/publish_tes.py (glob {unit_id}_*_PUBLIC.zip) and
    # publish_tpt.py --part bundle (looks for {unit_id}_v001_BUNDLE.zip)
    # all resolve this bundle's zip with zero code changes.
    public_path = ARTIFACTS_ROOT / f"{bundle_id}_{version}_PUBLIC.zip"
    bundle_path = ARTIFACTS_ROOT / f"{bundle_id}_{version}_BUNDLE.zip"

    with zipfile.ZipFile(public_path, "w", zipfile.ZIP_DEFLATED) as out_zf:
        for unit_id in unit_ids:
            src = _packaged_zip(unit_id, version)
            with zipfile.ZipFile(src) as in_zf:
                for info in in_zf.infolist():
                    if info.is_dir():
                        continue
                    data = in_zf.read(info.filename)
                    # Namespace every entry under <unit_id>/ so two units'
                    # identically-numbered lesson files never collide.
                    out_zf.writestr(f"{unit_id}/{info.filename}", data)

    with zipfile.ZipFile(public_path) as zf:
        bad = zf.testzip()
        if bad is not None:
            raise RuntimeError(f"Corrupt entry in {public_path.name}: {bad}")

    bundle_path.write_bytes(public_path.read_bytes())
    return public_path


def build_listing(bundle_id: str, title: str, unit_ids: list[str],
                   price_aud: str | None, price_gbp: str | None) -> dict[str, Path]:
    """Writes releases/<bundle_id>/listings/unit/{tpt,gumroad,tes}_listing.md
    in the exact format each publish script's own _read_listing()/
    read_tpt_listing() already expects (line 1 = "# Title", the rest =
    description) -- so `--unit <bundle_id>` on any of the three publish
    scripts resolves title/description with zero code changes, the same
    way the zip resolves via the _PUBLIC.zip/_BUNDLE.zip naming above.
    Also writes a human-readable copy to data/units/marketing/ for
    reference (not read by any publish script).

    TPT's markdown listing path has no price field of its own --
    publish_tpt.py's `--part bundle` reads price from the TPT_BUNDLE_PRICE
    env var (default $12.99, calibrated for a single unit) -- override it
    explicitly for a multi-unit bundle rather than relying on that default.
    """
    configs = [_load_unit_config(u) for u in unit_ids]

    included_lines = []
    outcome_lines = []
    for cfg in configs:
        unit_title = cfg.get("title", cfg["unit_id"])
        topics = cfg.get("topics", [])
        included_lines.append(f"- **{unit_title}** — 7 lessons + assessment pack")
        for t in topics:
            outcome_lines.append(f"  - {t.get('title', t) if isinstance(t, dict) else t}")

    n_units = len(unit_ids)
    n_lessons = sum(len(cfg.get("topics", [])) for cfg in configs)
    display_title = f"{title} — {n_units}-Unit Digital Technologies Bundle ({n_lessons} Lessons Total)"
    short_desc = (
        f"Save time and money with this {n_units}-unit bundle: "
        + " + ".join(cfg.get("title", cfg["unit_id"]).split(":")[0] for cfg in configs)
        + f". {n_lessons} ready-to-teach lessons, full assessment packs, "
        "student workbooks, and teacher guides -- no prep required."
    )
    why_line = (
        f"Bundling these {n_units} units together costs less than buying each "
        "unit's bundle individually -- same content, no prep difference, "
        "just fewer separate purchases and a lower total price."
    )

    body_lines = [
        short_desc,
        "",
        "What's included:",
        "",
        *included_lines,
        "",
        "Lesson outcomes covered:",
        "",
        *outcome_lines,
        "",
        "Why bundle over buying separately:",
        why_line,
    ]

    listing_text = "\n".join([f"# {display_title}", "", *body_lines])

    RELEASES_ROOT = ARTIFACTS_ROOT.parent
    bundle_unit_root = RELEASES_ROOT / bundle_id / "listings" / "unit"
    bundle_unit_root.mkdir(parents=True, exist_ok=True)
    written = {}
    for platform in ("tpt_listing.md", "gumroad_listing.md", "tes_listing.md"):
        p = bundle_unit_root / platform
        p.write_text(listing_text, encoding="utf-8")
        written[platform] = p

    # Human-readable reference copy, with the actual prices noted (the
    # per-platform files above deliberately don't embed price -- each
    # publish script sources price from its own --price arg or env var).
    price_line = ""
    if price_aud:
        price_line += f"AUD ${price_aud}"
    if price_gbp:
        price_line += (" / " if price_line else "") + f"GBP £{price_gbp}"
    ref_lines = [
        f"# Bundle listing — {title}",
        "",
        f"Bundle ID: `{bundle_id}`",
        f"Price: {price_line or '[SET PRICE]'} (TPT price set separately via TPT_BUNDLE_PRICE env var)",
        f"Zip: releases/artifacts/{bundle_id}_v001_BUNDLE.zip",
        "",
        f"## {display_title}",
        "",
        *body_lines,
        "",
    ]
    MARKETING_ROOT.mkdir(parents=True, exist_ok=True)
    ref_path = MARKETING_ROOT / f"{bundle_id}_listing.md"
    ref_path.write_text("\n".join(ref_lines), encoding="utf-8")
    written["reference"] = ref_path
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Combine 2-3 units' persisted zips into one bundle product + template listing."
    )
    parser.add_argument("--bundle-id", required=True, help="e.g. programming_foundations_bundle")
    parser.add_argument("--title", required=True, help="e.g. 'Programming Foundations Bundle'")
    parser.add_argument("--units", nargs="+", required=True, help="2-3 unit_ids to combine")
    parser.add_argument("--version", default="v001")
    parser.add_argument("--price-aud", default=None)
    parser.add_argument("--price-gbp", default=None)
    args = parser.parse_args()

    if not (2 <= len(args.units) <= 3):
        print("ERROR: pass 2 or 3 --units (bundles bigger than that need the "
              "separate curriculum-bundle initiative, not this script).")
        sys.exit(1)

    try:
        zip_path = build_bundle_zip(args.bundle_id, args.units, args.version)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    listing_paths = build_listing(args.bundle_id, args.title, args.units,
                                   args.price_aud, args.price_gbp)

    print(f"Bundle zip built : {zip_path} ({zip_path.stat().st_size:,} bytes)")
    print(f"                   (+ matching _BUNDLE.zip alongside it, for TPT)")
    print(f"Listings written : releases/{args.bundle_id}/listings/unit/"
          "{tpt,gumroad,tes}_listing.md")
    print(f"Reference copy   : {listing_paths['reference']}")
    print(
        f"\nNext step -- publish with the existing scripts, using --unit {args.bundle_id} "
        "(the bundle id doubles as a pseudo unit_id, so each script's normal "
        "zip AND listing auto-discovery both just find it -- no --zip or "
        "manual copy-paste needed):\n"
        f"  TPT_BUNDLE_PRICE=<USD price> python publish_tpt.py --unit {args.bundle_id} "
        "--part bundle --tags \"...\" --publish\n"
        "    (TPT's markdown listing path has no price field of its own -- "
        "it always reads TPT_BUNDLE_PRICE, calibrated for a single unit "
        "in .env, so override it for this one call)\n"
        f"  python publish_gumroad.py --unit {args.bundle_id} --price {args.price_aud or '<AUD>'}\n"
        f"  python publish_tes.py --unit {args.bundle_id} --price {args.price_gbp or '<GBP>'} --publish"
    )


if __name__ == "__main__":
    main()

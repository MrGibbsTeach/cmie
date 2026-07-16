"""
generate_marketing_content.py — produce ready-to-post marketing copy for a
unit: Pinterest pins (the dominant external traffic source for TPT
sellers), short social captions, and a longer Facebook teacher-group post.

Deliberately template-based, not an OpenAI call -- this is copy, not new
lesson content, and doesn't need per-unit AI generation cost to be good.
Uses the same topic-keyword extraction as the listing generator so the
tone/wording stays consistent with what's already on the live listings.

Output is a single markdown file per unit under
releases/public/<unit>_v001/07_Marketing/marketing_content.md -- text only,
nothing is posted anywhere. Posting is a human decision, same as
publishing.

Usage:
    python generate_marketing_content.py --unit year7_web_design_unit1
    python generate_marketing_content.py --all
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DATA_UNITS = PROJECT_ROOT / "data" / "units"
RELEASES_PUBLIC = PROJECT_ROOT / "releases" / "public"
BUNDLE_URLS_FILE = DATA_UNITS / "bundle_urls.json"

STORE_NAME = "FocusLab Digital"


def _load_bundle_urls() -> dict:
    if BUNDLE_URLS_FILE.exists():
        return json.loads(BUNDLE_URLS_FILE.read_text(encoding="utf-8"))
    return {}


def _topic_keyword(title: str) -> str:
    return title.split(":")[0].strip() if ":" in title else title.strip()


def _grade_terms(year_level: str) -> str:
    mapping = {
        "lower secondary": "Year 7 / Grade 7 / Middle School / KS3",
        "upper secondary": "Year 10 / Grade 10 / High School / KS4",
    }
    return mapping.get(year_level.strip().lower(), year_level)


def _read_lesson_titles(unit_id: str) -> list[str]:
    """Use the config's own authored topic titles ("How the Web Works:
    Browsers, Servers, and Requests") rather than reconstructing from
    slugified pptx filenames, which naively .title()-cases every word
    ("How The Web Works Browsers...") and reads worse than the real thing."""
    cfg_path = DATA_UNITS / f"{unit_id}.json"
    if not cfg_path.exists():
        return []
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    return [t["title"] for t in cfg.get("topics", [])]


def build_pinterest_pins(topic: str, title: str, grade: str, bundle_url: str, lesson_count: int) -> list[dict]:
    return [
        {
            "title": f"{topic} Unit for {grade.split('/')[0].strip()} — No-Prep Digital Technologies",
            "description": (
                f"Teach {topic.lower()} with zero prep! A complete {lesson_count}-lesson unit including "
                f"editable slides, student workbook, assessment + rubric, and unit roadmap. "
                f"Perfect for {grade} Digital Technologies / Computer Science teachers. "
                f"#teacherspayteachers #digitaltechnologies #middleschoolcs #{topic.lower().replace(' ', '').replace('&', '')} "
                f"#{'y7' if 'Year 7' in grade else 'ks3'}"
            ),
            "link": bundle_url,
        },
        {
            "title": f"{lesson_count} Ready-to-Teach {topic} Lessons — Editable PPTX",
            "description": (
                f"Stop building {topic.lower()} lessons from scratch. This bundle has everything: "
                f"{lesson_count} fully planned lessons, a real-world applied project, and a full assessment pack. "
                f"Grab the free sample lesson first to see the quality before you buy the bundle. "
                f"#tptseller #computersciencelessons #digitaltech"
            ),
            "link": bundle_url,
        },
        {
            "title": f"FREE {topic} Lesson Sample (Try Before You Buy)",
            "description": (
                f"Try Lesson 1 of our {topic} unit completely free — a full, ready-to-teach PowerPoint deck, "
                f"no prep required. If it's useful, the complete {lesson_count}-lesson unit (with workbook, "
                f"roadmap, and assessment pack) is linked in the resource. "
                f"#freeteacherresource #tpt #digitaltechnologies"
            ),
            "link": bundle_url,
        },
    ]


def build_social_captions(topic: str, title: str, bundle_url: str) -> list[str]:
    return [
        f"New resource alert 📚 A complete, no-prep {topic} unit is live — full lesson decks, "
        f"student workbook, and an assessment pack ready to go. Link in bio / {bundle_url}",
        f"Teaching {topic.lower()} this term? Save yourself the lesson-planning weekend — "
        f"grab the free Lesson 1 sample and see if it's a fit for your class. {bundle_url}",
        f"Just published: {title.split(':')[0]} 🖥️ — {STORE_NAME} on TPT. "
        f"Built for real classrooms, no fluff. {bundle_url}",
    ]


def build_facebook_group_post(topic: str, title: str, bundle_url: str, lesson_count: int, lesson_titles: list[str]) -> str:
    lessons_preview = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(lesson_titles[:7]))
    return f"""Hi all! Sharing a resource in case it's useful for anyone teaching {topic} this term.

I put together a complete {lesson_count}-lesson unit — "{title}" — with fully editable PowerPoint decks, a student workbook, unit roadmap, and a summative assessment pack with rubric. No prep needed, just teach.

Lessons cover:
{lessons_preview}

There's a free sample of Lesson 1 if you want to check the quality before committing to the full bundle: {bundle_url}

Would love any feedback if you try it out — genuinely happy to tweak things based on what actually works in your classroom. Thanks for reading!"""


def build_tpt_follower_note(topic: str, title: str, bundle_url: str) -> str:
    return f"""Subject: New unit just published — {topic}

Hi everyone,

Just published a new complete unit: "{title}". It includes 7 fully planned lessons, editable slide decks, a student workbook, unit roadmap, and a full assessment pack with rubric.

There's also a free Lesson 1 sample if you'd like to try before buying the bundle.

Check it out here: {bundle_url}

Thanks for following the store — more units on the way!
"""


def generate_for_unit(unit_id: str, version: str = "v001") -> Path:
    cfg_path = DATA_UNITS / f"{unit_id}.json"
    if not cfg_path.exists():
        raise FileNotFoundError(f"No config found for {unit_id}: {cfg_path}")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    title = cfg["title"]
    topic = _topic_keyword(title)
    grade = _grade_terms(cfg.get("year_level", ""))
    lesson_count = len(cfg.get("topics", [])) or 7
    lesson_titles = _read_lesson_titles(unit_id)

    bundle_urls = _load_bundle_urls()
    bundle_url = bundle_urls.get(unit_id, "[PASTE BUNDLE URL HERE]")

    pins = build_pinterest_pins(topic, title, grade, bundle_url, lesson_count)
    captions = build_social_captions(topic, title, bundle_url)
    fb_post = build_facebook_group_post(topic, title, bundle_url, lesson_count, lesson_titles)
    follower_note = build_tpt_follower_note(topic, title, bundle_url)

    lines = [f"# Marketing content — {title}", ""]
    lines.append(f"Bundle URL: {bundle_url}")
    lines.append("")
    lines.append("## Pinterest pins (make 3 separate pins, one image each — reuse the thumbnail or a slide screenshot)")
    lines.append("")
    for i, pin in enumerate(pins, 1):
        lines.append(f"### Pin {i}")
        lines.append(f"**Title** ({len(pin['title'])} chars): {pin['title']}")
        lines.append("")
        lines.append(f"**Description**: {pin['description']}")
        lines.append("")
        lines.append(f"**Link**: {pin['link']}")
        lines.append("")

    lines.append("## Social captions (Instagram / Facebook page / Twitter-X)")
    lines.append("")
    for i, cap in enumerate(captions, 1):
        lines.append(f"{i}. {cap}")
        lines.append("")

    lines.append("## Facebook teacher-group post (longer, conversational — check each group's self-promo rules first)")
    lines.append("")
    lines.append(fb_post)
    lines.append("")

    lines.append("## TPT \"Note to Followers\" draft (post via Inbox > Sent on TPT — free, reaches existing followers)")
    lines.append("")
    lines.append(follower_note)

    out_dir = RELEASES_PUBLIC / f"{unit_id}_{version}" / "07_Marketing"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "marketing_content.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", help="Single unit ID")
    parser.add_argument("--all", action="store_true", help="Generate for every unit listed in bundle_urls.json")
    parser.add_argument("--version", default="v001")
    args = parser.parse_args()

    if args.all:
        bundle_urls = _load_bundle_urls()
        for unit_id in bundle_urls:
            try:
                out = generate_for_unit(unit_id, args.version)
                print(f"{unit_id}: {out}")
            except Exception as e:
                print(f"{unit_id}: ERROR {e}")
        return

    if not args.unit:
        parser.error("--unit or --all is required")

    out = generate_for_unit(args.unit, args.version)
    print(f"Written: {out}")


if __name__ == "__main__":
    main()

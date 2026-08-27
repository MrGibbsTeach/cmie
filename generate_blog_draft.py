"""
generate_blog_draft.py -- drafts a blog post for the marketing-site/ blog,
reusing this project's existing content-generation pattern (same OpenAI
client/model as cmie/generator/ai_lesson_engine.py).

Deliberately does NOT publish anything. Writes to marketing-site/content/
blog_drafts/<slug>.md for human review -- move the file into
marketing-site/content/blog/ (dropping "_drafts") once approved, then
redeploy. This mirrors the same draft-then-review pattern already used for
Gumroad/TES drafts elsewhere in this project, not a new gate being
invented here.

Usage:
    python generate_blog_draft.py --topic "how to teach algorithms without a computer"
    python generate_blog_draft.py --topic "..." --keyword "unplugged coding activities"
"""
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from openai import OpenAI

DRAFTS_DIR = Path("marketing-site/content/blog_drafts")
SITE_BASE = "https://focuslab-marketing3.vercel.app"


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def draft_post(topic: str, keyword: str | None = None) -> tuple[str, str, str]:
    """Returns (title, description, markdown_body)."""
    client = OpenAI()
    target_phrase = keyword or topic

    prompt = f"""Write a blog post for Digital Technologies teachers (Years 7-10,
US/UK/AU curricula) on this topic: "{topic}".

The post should naturally target the search phrase "{target_phrase}" without
keyword-stuffing. Write like a real teacher-author sharing genuine classroom
experience, not marketing copy. 500-800 words. Include 2-3 concrete, specific
examples or activities a teacher could use tomorrow, not generic advice.
End with a short, natural mention that FocusLab Digital has free lesson
samples, without being pushy. Include exactly one real markdown link in
that closing mention: [free lesson samples]({SITE_BASE}/) -- use that
literal URL, not a placeholder.

Respond with exactly this structure:
TITLE: <a specific, human title, not clickbait>
DESCRIPTION: <one sentence, for a search-result snippet>
---
<the post body in markdown, no title heading repeated at the top>
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content or ""

    title_match = re.search(r"TITLE:\s*(.+)", text)
    desc_match = re.search(r"DESCRIPTION:\s*(.+)", text)
    body = text.split("---", 1)[-1].strip()

    title = title_match.group(1).strip() if title_match else topic
    description = desc_match.group(1).strip() if desc_match else ""
    return title, description, body


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True, help="What the post is about")
    parser.add_argument("--keyword", help="Search phrase to target (defaults to --topic)")
    args = parser.parse_args()

    title, description, body = draft_post(args.topic, args.keyword)
    slug = slugify(title)

    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DRAFTS_DIR / f"{slug}.md"
    out_path.write_text(
        f"""---
title: "{title}"
description: "{description}"
date: "{date.today().isoformat()}"
---

{body}
""",
        encoding="utf-8",
    )

    print(f"Draft written: {out_path}")
    print(f"Title: {title}")
    print(f"Description: {description}")
    print()
    print("Review the draft, then move it to marketing-site/content/blog/")
    print("(dropping the _drafts suffix) and redeploy when ready to publish.")


if __name__ == "__main__":
    main()

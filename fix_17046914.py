"""
fix_17046914.py -- one-off fix for TPT product 17046914 ("Images, Links &
Lists | Unit 1 - Building Your First Website | Lesson 3"), the sole product
retag_tpt_catalog.py could not edit.

Root cause (found 2026-09-27): the stored description contains literal,
unescaped tag mentions -- "<img>", "<a>", "<ol>", "<ul>", "<li>" -- written
as plain text ("Insert images with <img> using src and alt attributes.").
TPT's edit page feeds that HTML straight into a Lexical rich-text editor,
which throws (minified error #66 -- an unterminated/void element it can't
turn into an editable node) and never mounts. Since the whole edit form is
one React tree, that same crash silently breaks the Submit handler too --
not reCAPTCHA, not a validation error, just a dead component tree with no
visible error.

This is also a genuine pre-existing bug on the LIVE public listing, unrelated
to this session's changes: a browser renders "<img>" inside a <span> as a
void element with no text, so the buyer-facing description already reads
"Insert images with  using src and alt attributes." -- the tag name silently
vanished. Confirmed via the raw GraphQL response, not just the visible page.

Fix: intercept the page's own UploadPageProductQuery/Products GraphQL
responses and rewrite the description's literal "<tag>" mentions to
"the <tag> tag" with the brackets removed (e.g. "the img tag") before the
page's JS ever sees them. That lets the editor mount normally, and the
corrected wording -- not the original broken markup -- is what gets saved
back, fixing the live description at the same time as the retag.

Usage:
    python fix_17046914.py --dry-run
    python fix_17046914.py
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

from dotenv import load_dotenv

load_dotenv()

PID = "17046914"

# Exact known-broken phrases only -- NOT a blanket "<ul>"/"<li>" substitution.
# The description's real list markup uses the identical tag names
# ("<ul><li>...") as the literal, unescaped mentions inside the text
# ("...with <li> items."), so a bare-tag regex corrupts the genuine
# structure along with the broken text. Matching the full known phrase
# (captured from the live GraphQL response, 2026-09-27) only ever hits the
# three broken bullet lines, never the real <ul>/<li>/<ol> wrapping them.
PHRASE_FIXES = [
    ("Insert images with <img> using src and alt attributes.",
     "Insert images using the img tag with src and alt attributes."),
    ("Design clickable links with <a> and href.",
     "Design clickable links using the a tag and the href attribute."),
    ("Build ordered (<ol>) and unordered (<ul>) lists with <li> items.",
     "Build ordered and unordered lists using the ol, ul, and li tags."),
]


def clean_description(desc: str) -> str:
    for old, new in PHRASE_FIXES:
        desc = desc.replace(old, new)
    return desc


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    import retag_tpt_catalog as retag
    from cmie.publishing.browser import automation_chrome
    from cmie.publishing.tpt import _login

    def route_handler(route):
        req = route.request
        if req.method != "POST" or "graph/graphql" not in req.url:
            route.continue_()
            return
        response = route.fetch()
        try:
            body = response.json()
        except Exception:
            route.fulfill(response=response)
            return
        changed = False

        def _walk(obj):
            nonlocal changed
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, str) and any(old in v for old, _ in PHRASE_FIXES):
                        obj[k] = clean_description(v)
                        changed = True
                    elif isinstance(v, (dict, list)):
                        _walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    _walk(item)

        _walk(body)
        if changed:
            print("Rewrote a GraphQL response's description field to unbreak the editor.", flush=True)
        route.fulfill(response=response, json=body)

    with automation_chrome() as (ctx, page):
        _login(page, ctx, os.environ.get("TPT_EMAIL", ""), os.environ.get("TPT_PASSWORD", ""))
        page.route("**/graph/graphql*", route_handler)

        st = retag.read_state(page, PID)
        print("has_editor:", st["has_editor"])
        if not st["has_editor"]:
            print("Editor still did not mount -- aborting, no changes made.")
            sys.exit(1)
        print("DESC_NOW:", st["desc"][:400].replace("\n", " | "))

        units = retag.load_units()
        plan = retag.plan_for(units, st)
        print("PLAN:", json.dumps(plan, indent=1))

        if args.dry_run:
            print("Dry run -- stopping before any edit.")
            return

        status = retag.apply_and_verify(page, PID, plan)
        print("RESULT:", status)

        log = retag.load_log()
        log[PID] = {"status": status, **plan}
        retag.save_log(log)


if __name__ == "__main__":
    main()

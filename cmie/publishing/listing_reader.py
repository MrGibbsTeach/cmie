"""
Parse TPT listing files from a unit release folder.
Handles both formats:
  - Structured key:value  (unit 1 bundle_listings/tpt_listing.txt)
  - Markdown              (units 2-8 listings/unit/tpt_listing.md)
"""
from __future__ import annotations

import os
import re
from pathlib import Path


def _parse_structured(text: str) -> dict:
    result: dict = {}
    current_key: str | None = None
    current_val: list[str] = []

    for line in text.splitlines():
        m = re.match(r'^([A-Z][A-Z ]+):\s*(.*)$', line)
        if m:
            if current_key:
                result[current_key] = '\n'.join(current_val).strip()
            current_key = m.group(1).strip()
            val = m.group(2).strip()
            current_val = [val] if val else []
        elif current_key:
            current_val.append(line)

    if current_key:
        result[current_key] = '\n'.join(current_val).strip()

    return result


def _parse_markdown(text: str, tags: str | None = None) -> dict:
    lines = text.strip().splitlines()
    title = lines[0].lstrip('#').strip() if lines else ''
    return {
        'TITLE': title,
        'DESCRIPTION': text.strip(),
        'PRICE': os.getenv('TPT_DEFAULT_PRICE', '29.99'),
        'TAGS': tags or 'Digital Technologies, Lower secondary, No prep, STEM, Computers, Year 7, Year 8, Year 9',
    }


def read_tpt_listing_from_markdown(md_path: Path, price: float | None = None, tags: str | None = None) -> dict:
    """Build a TPT listing dict from an arbitrary markdown listing file
    (e.g. a per-lesson or assessment listing), not just the unit-level one."""
    raw = _parse_markdown(md_path.read_text(encoding='utf-8'), tags=tags)
    if price is not None:
        raw['PRICE'] = str(price)

    title = raw.get('TITLE', '').strip()
    if len(title) > 80:
        title = title[:80].rsplit(' ', 1)[0]

    return {
        'title': title,
        'description': raw.get('DESCRIPTION', '').strip(),
        'price': float(raw.get('PRICE', '29.99')),
        'tags': [t.strip() for t in raw.get('TAGS', '').split(',') if t.strip()],
    }


def read_tpt_listing(unit_folder: Path) -> dict:
    """
    Returns: {title, description, price (float), tags (list[str])}
    """
    structured_path  = unit_folder / 'bundle_listings' / 'tpt_listing.txt'
    md_path          = unit_folder / 'listings' / 'unit' / 'tpt_listing.md'
    public_md_path   = unit_folder / '06_Listings' / 'unit' / 'tpt_listing.md'

    if structured_path.exists():
        raw = _parse_structured(structured_path.read_text(encoding='utf-8'))
    elif md_path.exists():
        raw = _parse_markdown(md_path.read_text(encoding='utf-8'))
    elif public_md_path.exists():
        raw = _parse_markdown(public_md_path.read_text(encoding='utf-8'))
    else:
        raise FileNotFoundError(
            f"No TPT listing found in {unit_folder}. "
            f"Expected {structured_path} or {md_path}"
        )

    # The structured parser splits sub-headers (WHAT YOU GET, WHY THIS WORKS, etc.)
    # into separate keys. Reassemble them into one full description.
    DESCRIPTION_SECTIONS = [
        'WHAT YOU GET', 'WHAT YOU GET', 'STUDENT OUTCOMES',
        'WHY THIS WORKS', 'PERFECT FOR',
    ]
    desc = raw.get('DESCRIPTION', '').strip()
    for section in ['WHAT YOU GET', 'STUDENT OUTCOMES', 'WHY THIS WORKS', 'PERFECT FOR']:
        if section in raw and raw[section]:
            desc += f'\n\n{section}:\n{raw[section]}'

    # TPT title field has an ~80 char limit — truncate cleanly at a word boundary
    title = raw.get('TITLE', '').strip()
    if len(title) > 80:
        title = title[:80].rsplit(' ', 1)[0]

    return {
        'title': title,
        'description': desc,
        'price': float(raw.get('PRICE', '29.99')),
        'tags': [t.strip() for t in raw.get('TAGS', '').split(',') if t.strip()],
    }

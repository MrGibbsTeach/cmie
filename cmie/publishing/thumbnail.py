"""
Generate a branded TPT product cover image (1500x1125, 4:3).
Uses Pillow with system fonts (Segoe UI or Arial fallback).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

W, H = 1500, 1125

# Palette — light base, bold indigo header
BG_WHITE   = (255, 255, 255)
BG_LIGHT   = (246, 247, 254)   # faint indigo tint
HEADER_BG  = (49,  46,  129)   # indigo-900
HEADER_MID = (79,  70,  229)   # indigo-600
ACCENT     = (99,  102, 241)   # indigo-500
CARD_BG    = (238, 242, 255)   # indigo-50
CARD_ICON  = (67,  56,  202)   # indigo-700
TEXT_DARK  = (17,  24,  39)    # gray-900
TEXT_MED   = (75,  85,  99)    # gray-600
TEXT_LIGHT = (148, 163, 184)   # slate-400
WHITE      = (255, 255, 255)
GREEN      = (5,   150, 105)   # emerald-600


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        f"C:/Windows/Fonts/{'segoeuib' if bold else 'segoeui'}.ttf",
        f"C:/Windows/Fonts/{'arialbd'  if bold else 'arial'}.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_w: int, draw: ImageDraw.Draw) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur: list[str] = []
    for word in words:
        test = " ".join(cur + [word])
        if draw.textlength(test, font=font) > max_w and cur:
            lines.append(" ".join(cur))
            cur = [word]
        else:
            cur.append(word)
    if cur:
        lines.append(" ".join(cur))
    return lines


def generate_thumbnail(
    title: str,
    config: dict,
    output_dir: Path,
    includes: Optional[list[str]] = None,
) -> Path:
    """
    Create a branded PNG cover image for a TPT listing.
    Returns the path to the saved file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    unit_id    = config.get("unit_id", "unit")
    year_level = config.get("year_level", "")
    subject    = config.get("subject", "Digital Technologies")

    if includes is None:
        includes = [
            "7 fully planned lessons",
            "Student workbook (print or digital)",
            "Summative assessment + rubric",
            "Teacher guide + unit roadmap",
        ]

    HEADER_H = int(H * 0.46)   # top 46% = colour band

    img  = Image.new("RGB", (W, H), BG_WHITE)
    draw = ImageDraw.Draw(img)

    # ------------------------------------------------------------------ #
    # HEADER BAND
    # ------------------------------------------------------------------ #
    draw.rectangle([0, 0, W, HEADER_H], fill=HEADER_BG)

    # Subtle diagonal accent stripe inside header
    for i in range(0, 8):
        x = W - 320 + i * 42
        draw.polygon([(x, 0), (x + 280, 0), (x + 280 - HEADER_H, HEADER_H), (x - HEADER_H, HEADER_H)],
                     fill=HEADER_MID)

    # Re-clip header shape (polygon may bleed)
    draw.rectangle([0, HEADER_H, W, H], fill=BG_WHITE)

    # Subject badge
    f_badge = _font(26)
    bx, by = 52, 46
    btext = subject.upper()
    bw = int(draw.textlength(btext, font=f_badge)) + 40
    draw.rounded_rectangle([bx, by, bx + bw, by + 46], radius=6, fill=ACCENT)
    draw.text((bx + 20, by + 10), btext, font=f_badge, fill=WHITE)

    # Year level tag
    if year_level:
        yx = bx + bw + 12
        yw = int(draw.textlength(year_level, font=f_badge)) + 40
        draw.rounded_rectangle([yx, by, yx + yw, by + 46], radius=6, fill=(255, 255, 255, 30))
        draw.rounded_rectangle([yx, by, yx + yw, by + 46], radius=6, outline=ACCENT, width=2, fill=(49, 46, 129))
        draw.text((yx + 20, by + 10), year_level, font=f_badge, fill=WHITE)

    # NO PREP badge top-right
    f_np = _font(26, bold=True)
    np_text = "NO PREP"
    np_w = int(draw.textlength(np_text, font=f_np)) + 44
    np_x = W - np_w - 44
    draw.rounded_rectangle([np_x, by, np_x + np_w, by + 46], radius=23, fill=GREEN)
    draw.text((np_x + 22, by + 10), np_text, font=f_np, fill=WHITE)

    # Series subtitle
    clean = re.sub(r"\s*\([^)]+\)\s*$", "", title).strip()
    if ":" in clean:
        series_part, topic_part = clean.split(":", 1)
        series_part = series_part.strip()
        topic_part  = topic_part.strip()
    else:
        series_part = ""
        topic_part  = clean

    ty = 130
    if series_part:
        f_series = _font(36)
        draw.text((56, ty), series_part, font=f_series, fill=TEXT_LIGHT)
        ty += 58

    # Main title
    f_title = _font(96, bold=True)
    for line in _wrap(topic_part, f_title, W - 112, draw)[:2]:
        draw.text((56, ty), line, font=f_title, fill=WHITE)
        ty += 112

    # Lesson count pill at bottom of header
    lesson_count = next((x for x in includes if "lesson" in x.lower()), None)
    if lesson_count:
        f_pill = _font(28, bold=True)
        pill_text = lesson_count.upper()
        pw = int(draw.textlength(pill_text, font=f_pill)) + 48
        py = HEADER_H - 54
        draw.rounded_rectangle([56, py, 56 + pw, py + 38], radius=19, fill=ACCENT)
        draw.text((56 + 24, py + 6), pill_text, font=f_pill, fill=WHITE)

    # ------------------------------------------------------------------ #
    # LOWER SECTION — white background
    # ------------------------------------------------------------------ #

    # Section heading
    f_head = _font(30, bold=True)
    hy = HEADER_H + 36
    draw.text((56, hy), "WHAT'S INCLUDED", font=f_head, fill=TEXT_MED)

    # Thin accent underline
    hw = int(draw.textlength("WHAT'S INCLUDED", font=f_head))
    draw.rectangle([56, hy + 40, 56 + hw, hy + 43], fill=ACCENT)

    # 2-column card grid
    card_items = [x for x in includes if "lesson" not in x.lower()] + \
                 [x for x in includes if "lesson" in x.lower()]
    card_items = includes  # keep original order, all items

    COLS = 2
    CARD_W = (W - 112 - 20) // COLS
    CARD_H = 78
    GAP_X  = 20
    GAP_Y  = 16
    cx0    = 56
    cy0    = hy + 60

    f_card = _font(28)
    f_icon = _font(24, bold=True)

    for i, item in enumerate(card_items):
        if i >= 6:  # max 6 cards (3 rows × 2 cols)
            break
        col = i % COLS
        row = i // COLS
        cx = cx0 + col * (CARD_W + GAP_X)
        cy = cy0 + row * (CARD_H + GAP_Y)

        # Card background
        draw.rounded_rectangle([cx, cy, cx + CARD_W, cy + CARD_H], radius=10, fill=CARD_BG)

        # Icon square
        icon_x, icon_y = cx + 14, cy + 14
        draw.rounded_rectangle([icon_x, icon_y, icon_x + 50, icon_y + 50], radius=8, fill=CARD_ICON)
        num = str(i + 1)
        nw = draw.textlength(num, font=f_icon)
        draw.text((icon_x + (50 - nw) / 2, icon_y + 13), num, font=f_icon, fill=WHITE)

        # Item text — wrap inside card width
        text_x = cx + 78
        text_max = CARD_W - 88
        lines = _wrap(item, f_card, text_max, draw)
        text_y = cy + (CARD_H - len(lines) * 34) // 2
        for ln in lines[:2]:
            draw.text((text_x, text_y), ln, font=f_card, fill=TEXT_DARK)
            text_y += 34

    # ------------------------------------------------------------------ #
    # BOTTOM BRAND STRIP
    # ------------------------------------------------------------------ #
    strip_y = H - 70
    draw.rectangle([0, strip_y, W, H], fill=HEADER_BG)

    # Left: logo mark
    draw.rounded_rectangle([44, strip_y + 16, 72, strip_y + 54], radius=4, fill=ACCENT)
    f_brand = _font(30, bold=True)
    draw.text((84, strip_y + 18), "FocusLab Digital", font=f_brand, fill=WHITE)

    # Right: series name
    f_series_sm = _font(24)
    series_label = series_part if series_part else "Digital Technologies Resources"
    sl_w = draw.textlength(series_label, font=f_series_sm)
    draw.text((W - sl_w - 44, strip_y + 23), series_label, font=f_series_sm, fill=TEXT_LIGHT)

    out = output_dir / f"{unit_id}_thumbnail.png"
    img.save(str(out), "PNG")
    return out

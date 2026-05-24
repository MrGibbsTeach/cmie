from pathlib import Path
import json

from cmie.marketing.marketing_generator import generate_marketing_assets
from cmie.marketing.channel_renderer import generate_channel_files
from cmie.marketing.lesson_channel_renderer import generate_lesson_channel_files

unit_root = Path("releases/year7_ai_data_unit1")
lessons_dir = unit_root / "lessons"

unit_meta = {
    "unit_id": "year7_ai_data_unit1",
    "title": "AI & Data Literacy Series – Unit 1: Data Foundations",
    "year_level": "Lower Secondary",
    "subject": "Digital Technologies",
    "version": "v001",
}

print("Regenerating marketing assets...")
assets = generate_marketing_assets(unit_meta, lessons_dir)

marketing_path = unit_root / "marketing" / "marketing_assets.json"
marketing_path.parent.mkdir(parents=True, exist_ok=True)

with marketing_path.open("w", encoding="utf-8") as f:
    json.dump(assets, f, ensure_ascii=False, indent=2)

print(f"Saved marketing assets to: {marketing_path}")

print("Rendering unit listings...")
generate_channel_files(unit_root)

print("Rendering lesson listings...")
generate_lesson_channel_files(unit_root)

print("Done.")
print(f"Bundle listings: {unit_root / 'bundle_listings'}")
print(f"Lesson listings: {unit_root / 'lesson_listings'}")
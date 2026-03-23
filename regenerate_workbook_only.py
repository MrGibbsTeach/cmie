from pathlib import Path

from cmie.generator.workbook_generator import generate_student_workbook
from cmie.generator.canva_prompts import workbook_markdown_to_canva_prompt

unit_root = Path("releases/year7_ai_data_unit1")
lessons_dir = unit_root / "lessons"
assessment_dir = unit_root / "assessment"
workbook_dir = unit_root / "workbook"

print("Checking paths...")
print(f"unit_root: {unit_root.resolve()}")
print(f"lessons_dir exists: {lessons_dir.exists()}")
print(f"assessment_dir exists: {assessment_dir.exists()}")
print(f"workbook_dir exists before run: {workbook_dir.exists()}")

lesson_files = list(lessons_dir.glob("*.json"))
print(f"lesson json count: {len(lesson_files)}")
for path in lesson_files[:5]:
    print(f" - {path.name}")

unit_config = {
    "unit_id": "year7_ai_data_unit1",
    "title": "AI & Data Literacy Series – Unit 1: Data Foundations",
    "year_level": "Lower Secondary",
    "subject": "Digital Technologies",
    "version": "v001",
}

workbook_path = generate_student_workbook(
    unit_root=unit_root,
    unit_config=unit_config,
    lessons_dir=lessons_dir,
    assessment_dir=assessment_dir,
)

print(f"Workbook path returned: {workbook_path}")
print(f"Workbook exists after generation: {workbook_path.exists()}")

prompt_path = workbook_markdown_to_canva_prompt(workbook_path)

print(f"Canva prompt path returned: {prompt_path}")
print(f"Canva prompt exists after generation: {prompt_path.exists()}")
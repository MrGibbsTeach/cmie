from pathlib import Path
import logging

from cmie.pipeline.full_product_pipeline import markdown_to_docx

logger = logging.getLogger("workbook_docx_test")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

unit_root = Path("releases/year7_ai_data_unit1")
workbook_path = unit_root / "workbook" / "student_workbook.md"
output_path = unit_root / "PUBLIC_RELEASE_TEST" / "Student_Workbook.docx"

output_path.parent.mkdir(parents=True, exist_ok=True)

print(f"Input MD: {workbook_path.resolve()}")
print(f"Exists: {workbook_path.exists()}")

markdown_to_docx(
    workbook_path,
    output_path,
    logger,
)

print(f"DOCX generated at: {output_path.resolve()}")
print(f"Exists: {output_path.exists()}")
from pathlib import Path
from cmie.generator.slide_generator import lesson_json_to_canva_prompt

matches = list(Path("generated_lessons").rglob("data-shapes-the-ai-world/lesson.json"))

if not matches:
    raise FileNotFoundError("Could not find lesson.json for data-shapes-the-ai-world under generated_lessons")

lesson_path = matches[0]

print("Using lesson file:")
print(lesson_path)

result = lesson_json_to_canva_prompt(lesson_path)

print("Canva prompt created at:")
print(result)
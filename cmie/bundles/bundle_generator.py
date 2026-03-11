import json
from pathlib import Path
from typing import Dict, List, Any

from openai import OpenAI


def ensure_openai_client() -> OpenAI:
    return OpenAI()


def _load_marketing_files(unit_roots: List[Path]) -> List[Dict[str, Any]]:
    """
    Load marketing_assets.json from each unit root.
    """
    units = []

    for root in unit_roots:
        path = root / "marketing" / "marketing_assets.json"
        if not path.exists():
            raise FileNotFoundError(f"Missing marketing file: {path}")

        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        units.append(data)

    return units


def _build_bundle_prompt(bundle_name: str, units: List[Dict[str, Any]]) -> str:
    unit_summaries = []

    for u in units:
        unit_summaries.append(
            f"- {u.get('seo_title')}\n"
            f"  Includes: {', '.join(u.get('whats_included', []))}\n"
            f"  Learning outcomes: {', '.join(u.get('learning_outcomes', []))}\n"
        )

    unit_block = "\n".join(unit_summaries)

    return (
        "You are a curriculum marketplace strategist.\n\n"
        "Create high-converting marketing copy for a DIGITAL CURRICULUM BUNDLE.\n\n"
        "Respond ONLY in strict JSON using this schema:\n"
        "{\n"
        '  "bundle_title": string,\n'
        '  "bundle_subtitle": string,\n'
        '  "short_description": string,\n'
        '  "long_description": string,\n'
        '  "whats_included": [string],\n'
        '  "learning_outcomes": [string],\n'
        '  "ideal_for": [string],\n'
        '  "why_this_bundle": [string],\n'
        '  "pricing_strategy": string,\n'
        '  "recommended_price_aud": string\n'
        "}\n\n"
        "Rules:\n"
        "- Position this as a premium, complete solution.\n"
        "- Long description: 700–1000 words.\n"
        "- Pricing strategy must justify anchor pricing.\n"
        "- Assume Australian teacher marketplace context.\n\n"
        f'Bundle name: "{bundle_name}"\n\n'
        "Units included:\n"
        f"{unit_block}\n"
    )


def generate_bundle_marketing(
    bundle_name: str,
    unit_roots: List[Path],
    output_root: Path,
) -> Path:

    client = ensure_openai_client()

    units = _load_marketing_files(unit_roots)
    prompt = _build_bundle_prompt(bundle_name, units)

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You write high-converting curriculum marketing copy and respond ONLY with valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )

    raw = resp.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(raw[start:end + 1])
        else:
            raise

    bundle_root = output_root / bundle_name.replace(" ", "_").lower()
    bundle_root.mkdir(parents=True, exist_ok=True)

    out_path = bundle_root / "bundle_marketing.json"

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return out_path
import shutil
from pathlib import Path
from typing import Dict, Any


def package_release(
    unit_id: str,
    unit_root: Path,
    artifacts_root: Path,
    version: str = "v1",
) -> Dict[str, Any]:
    """
    Zip the entire release folder into an artifact ready for upload.
    """

    artifacts_root.mkdir(parents=True, exist_ok=True)

    archive_base = artifacts_root / f"{unit_id}_{version}"
    archive_path = shutil.make_archive(
        base_name=str(archive_base),
        format="zip",
        root_dir=str(unit_root),
    )

    return {
        "unit_id": unit_id,
        "artifact": archive_path,
    }
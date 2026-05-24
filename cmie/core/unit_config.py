from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import json


@dataclass
class TopicConfig:
    title: str
    video_url: Optional[str] = None


@dataclass
class UnitConfig:
    unit_id: str
    title: str
    year_level: str
    subject: str
    version: str = "v001"
    topics: List[TopicConfig] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnitConfig":
        topics_data = data.get("topics", [])
        topics = [
            TopicConfig(
                title=t["title"],
                video_url=t.get("video_url"),
            )
            for t in topics_data
        ]
        return cls(
            unit_id=data["unit_id"],
            title=data.get("title", data["unit_id"]),
            year_level=data.get("year_level", ""),
            subject=data.get("subject", ""),
            version=data.get("version", "v001"),
            topics=topics,
        )

    @classmethod
    def from_json_file(cls, path: Path) -> "UnitConfig":
        with path.open(encoding="utf-8") as f:
            raw = json.load(f)
        return cls.from_dict(raw)
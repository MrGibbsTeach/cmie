from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Job:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    type: str = "unit"            # unit | lesson | assessment
    status: str = "pending"       # pending | running | completed | failed
    title: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    output_path: Optional[str] = None
    download_zip: Optional[str] = None
    error: Optional[str] = None
    # Publishing
    publish_status: Optional[str] = None   # running | completed | failed
    publish_url: Optional[str] = None
    publish_error: Optional[str] = None
    thumbnail_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "title": self.title,
            "config": self.config,
            "logs": self.logs,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "output_path": self.output_path,
            "download_zip": self.download_zip,
            "error": self.error,
            "publish_status": self.publish_status,
            "publish_url": self.publish_url,
            "publish_error": self.publish_error,
            "thumbnail_path": self.thumbnail_path,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Job":
        def _dt(v: Any) -> Optional[datetime]:
            return datetime.fromisoformat(v) if v else None

        return cls(
            id=d["id"],
            type=d.get("type", "unit"),
            status=d.get("status", "pending"),
            title=d.get("title", ""),
            config=d.get("config", {}),
            logs=d.get("logs", []),
            created_at=_dt(d.get("created_at")) or datetime.utcnow(),
            completed_at=_dt(d.get("completed_at")),
            output_path=d.get("output_path"),
            download_zip=d.get("download_zip"),
            error=d.get("error"),
            publish_status=d.get("publish_status"),
            publish_url=d.get("publish_url"),
            publish_error=d.get("publish_error"),
            thumbnail_path=d.get("thumbnail_path"),
        )

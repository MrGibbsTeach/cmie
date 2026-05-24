import re
from typing import Optional

from sqlalchemy.orm import Session

from .models import Topic


# Expanded keyword → canonical topic mapping
TOPIC_KEYWORDS = {
    # Programming languages
    "python": "Programming - Python",
    "scratch": "Programming - Scratch",
    "java": "Programming - Java",
    "javascript": "Programming - JavaScript",
    "html": "Web Development",
    "css": "Web Development",

    # Broader CS / coding terms
    "computer science": "Computer Science - General",
    "cs": "Computer Science - General",
    "programming": "Programming - General",
    "coding": "Programming - General",

    # Other tech domains
    "cyber": "Cybersecurity",
    "digital citizenship": "Digital Citizenship",
    "algorithm": "Algorithms & Logic",
    "data": "Data & Analytics",
    "spreadsheet": "Spreadsheets",
}


def extract_topic_from_title(title: str) -> Optional[str]:
    """
    Infer canonical topic from listing title using keyword matching.
    Returns canonical topic name or None if no match found.
    """
    title_lower = title.lower()

    for keyword, topic_name in TOPIC_KEYWORDS.items():
        if keyword in title_lower:
            return topic_name

    return None


def get_or_create_topic(session: Session, topic_name: str) -> Topic:
    """
    Fetch topic from DB or create it if it does not exist.
    """
    topic = session.query(Topic).filter_by(name=topic_name).first()

    if topic:
        return topic

    topic = Topic(name=topic_name)
    session.add(topic)
    session.commit()

    return topic

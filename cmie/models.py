from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    Boolean,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True)
    marketplace = Column(Enum("tpt", "tes", name="marketplace_enum"), index=True)
    external_id = Column(String(128), index=True)
    url = Column(String(1024), nullable=False)
    title = Column(String(512), nullable=False)
    author = Column(String(256))
    description = Column(Text)
    subject_raw = Column(String(512))
    grade_levels_raw = Column(String(256))
    resource_type_raw = Column(String(256))
    price = Column(Float)
    currency = Column(String(8))
    rating_avg = Column(Float)
    rating_count = Column(Integer)

    is_bundle = Column(Boolean, default=False)
    has_video_preview = Column(Boolean, default=False)
    is_editable = Column(Boolean, default=False)
    has_standards_alignment = Column(Boolean, default=False)

    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        UniqueConstraint("marketplace", "external_id", name="uq_listing_marketplace_external"),
    )


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True, nullable=False)


class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    locale = Column(String(16))
    min_age = Column(Integer)
    max_age = Column(Integer)


class TopicStats(Base):
    __tablename__ = "topic_stats"

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    level_id = Column(Integer, ForeignKey("levels.id"))
    marketplace = Column(Enum("tpt", "tes", name="marketplace_enum"))

    listing_count = Column(Integer)
    avg_price = Column(Float)
    median_price = Column(Float)
    avg_rating = Column(Float)
    total_ratings = Column(Integer)
    demand_score = Column(Float)
    competition_score = Column(Float)
    moat_score = Column(Float)
    opportunity_score = Column(Float)

    last_computed_at = Column(DateTime, default=datetime.utcnow)


class TopicRecommendation(Base):
    __tablename__ = "topic_recommendations"

    id = Column(Integer, primary_key=True)
    topic_stats_id = Column(Integer, ForeignKey("topic_stats.id"))
    rank = Column(Integer)
    recommended_price = Column(Float)
    rationale = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

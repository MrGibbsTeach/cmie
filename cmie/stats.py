from collections import defaultdict
from statistics import mean, median
from math import log1p
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from .db import get_session_factory
from .config import DEFAULT_DB_URL
from .models import Listing, TopicStats
from .normalisation import extract_topic_from_title, get_or_create_topic


def _aggregate_topic_data(session: Session) -> Dict[str, Dict]:
    """
    Group listings by normalised topic name and aggregate simple stats.
    """
    listings: List[Listing] = session.query(Listing).all()

    agg: Dict[str, Dict] = defaultdict(
        lambda: {
            "prices": [],
            "ratings": [],
            "rating_counts": [],
            "listing_count": 0,
        }
    )

    for listing in listings:
        topic = extract_topic_from_title(listing.title)
        if not topic:
            continue

        bucket = agg[topic]
        bucket["listing_count"] += 1

        if listing.price is not None:
            bucket["prices"].append(listing.price)

        if listing.rating_avg is not None:
            bucket["ratings"].append(listing.rating_avg)

        if listing.rating_count is not None:
            bucket["rating_counts"].append(listing.rating_count)

    return agg


def _compute_scores(listing_count: int) -> Tuple[float, float, float, float]:
    """
    Compute rough demand / competition / moat / opportunity scores.

    These are simple heuristics for now:
    - demand_score: log-scaled listing_count
    - competition_score: proportional to listing_count
    - moat_score: inverse of competition (fewer competitors, higher moat)
    - opportunity_score: demand * moat (high demand, low competition)
    """
    if listing_count <= 0:
        return 0.0, 0.0, 0.0, 0.0

    demand_score = log1p(listing_count)  # log(1 + N)
    competition_score = float(listing_count)
    moat_score = 1.0 / (1.0 + competition_score)  # decays as competition grows
    opportunity_score = demand_score * moat_score

    return demand_score, competition_score, moat_score, opportunity_score


def compute_topic_stats_for_marketplace(marketplace: str = "tpt"):
    """
    Aggregate listings by topic and upsert rows into topic_stats table.
    Currently ignores levels (level_id left null).
    """
    Session = get_session_factory(DEFAULT_DB_URL)
    session = Session()

    agg = _aggregate_topic_data(session)

    for topic_name, data in agg.items():
        listing_count = data["listing_count"]
        prices = data["prices"]
        ratings = data["ratings"]
        rating_counts = data["rating_counts"]

        avg_price = mean(prices) if prices else None
        median_price = median(prices) if prices else None
        avg_rating = mean(ratings) if ratings else None
        total_ratings = int(sum(rating_counts)) if rating_counts else None

        demand_score, competition_score, moat_score, opportunity_score = _compute_scores(
            listing_count
        )

        # ensure Topic exists (for foreign key if we extend later)
        topic = get_or_create_topic(session, topic_name)

        # For now, we ignore level granularity and leave level_id = None
        stats_row = (
            session.query(TopicStats)
            .filter_by(
                topic_id=topic.id,
                level_id=None,
                marketplace=marketplace,
            )
            .first()
        )

        if not stats_row:
            stats_row = TopicStats(
                topic_id=topic.id,
                level_id=None,
                marketplace=marketplace,
            )
            session.add(stats_row)

        stats_row.listing_count = listing_count
        stats_row.avg_price = avg_price
        stats_row.median_price = median_price
        stats_row.avg_rating = avg_rating
        stats_row.total_ratings = total_ratings
        stats_row.demand_score = demand_score
        stats_row.competition_score = competition_score
        stats_row.moat_score = moat_score
        stats_row.opportunity_score = opportunity_score

    session.commit()
    session.close()

    print(f"Computed topic_stats for {len(agg)} topics (marketplace={marketplace}).")

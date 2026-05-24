from typing import List, Optional

from cmie.db import get_session_factory
from cmie.config import DEFAULT_DB_URL
from cmie.models import Topic, TopicStats


def simple_topic_summary():
    """
    Still available as a quick, in-memory snapshot (uses Listing directly).
    """
    from collections import defaultdict
    from statistics import mean
    from cmie.models import Listing
    from cmie.normalisation import extract_topic_from_title

    Session = get_session_factory(DEFAULT_DB_URL)
    session = Session()

    listings: List[Listing] = session.query(Listing).all()

    topic_counts = defaultdict(int)
    topic_prices = defaultdict(list)

    for listing in listings:
        topic = extract_topic_from_title(listing.title)
        if not topic:
            continue

        topic_counts[topic] += 1

        if listing.price is not None:
            topic_prices[topic].append(listing.price)

    print("Topic Demand Snapshot")
    print("----------------------------------------")

    if not topic_counts:
        print("No topics could be inferred yet.")
        session.close()
        return

    for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
        prices = topic_prices.get(topic, [])

        if prices:
            avg_price = round(mean(prices), 2)
            price_str = f"Avg Price=${avg_price}"
        else:
            price_str = "Avg Price=n/a"

        print(f"{topic}: Count={count}, {price_str}")

    session.close()


def recommend_topics(
    marketplace: str = "tpt", top_n: int = 5, min_listing_count: int = 3
):
    """
    Use topic_stats to recommend which topics to build next and at what price.
    """
    Session = get_session_factory(DEFAULT_DB_URL)
    session = Session()

    q = (
        session.query(TopicStats, Topic)
        .join(Topic, TopicStats.topic_id == Topic.id)
        .filter(TopicStats.marketplace == marketplace)
        .filter(TopicStats.listing_count >= min_listing_count)
        .order_by(TopicStats.opportunity_score.desc())
    )

    rows: List[tuple[TopicStats, Topic]] = q.limit(top_n).all()

    if not rows:
        print("No topic_stats rows found. Run compute_topic_stats_for_marketplace() first.")
        session.close()
        return

    print(f"Top {len(rows)} topic opportunities (marketplace={marketplace})")
    print("------------------------------------------------------------------")

    for rank, (stats_row, topic) in enumerate(rows, start=1):
        suggested_price: Optional[float]

        # Heuristic: if we have median_price, use that; else avg_price; else default band
        if stats_row.median_price is not None:
            suggested_price = stats_row.median_price
        elif stats_row.avg_price is not None:
            suggested_price = stats_row.avg_price
        else:
            # If we have no price data at all yet, fall back to a sensible default for digital curriculum
            suggested_price = 8.0

        suggested_price = round(suggested_price, 2)

        print(
            f"{rank}. {topic.name}\n"
            f"   Listings: {stats_row.listing_count}\n"
            f"   Demand score: {round(stats_row.demand_score, 3)}\n"
            f"   Competition score: {round(stats_row.competition_score, 3)}\n"
            f"   Moat score: {round(stats_row.moat_score, 3)}\n"
            f"   Opportunity score: {round(stats_row.opportunity_score, 3)}\n"
            f"   Suggested price: ${suggested_price}\n"
        )

    session.close()

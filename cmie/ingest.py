from cmie.connectors.tpt import TPTConnector
from cmie.db import get_session_factory
from cmie.config import DEFAULT_DB_URL
from cmie.models import Listing


def ingest_tpt(query: str, page: int = 1):
    connector = TPTConnector()
    listings = connector.fetch_listings(query=query, page=page)

    Session = get_session_factory(DEFAULT_DB_URL)
    session = Session()

    inserted = 0

    for item in listings:
        # Check duplicate by external_id + marketplace
        exists = (
            session.query(Listing)
            .filter_by(
                external_id=item["external_id"],
                marketplace=item["marketplace"],
            )
            .first()
        )

        if exists:
            continue

        listing = Listing(
            marketplace=item["marketplace"],
            external_id=item["external_id"],
            url=item["url"],
            title=item["title"],
            author=item.get("author"),
            description=item.get("description"),
            price=item.get("price"),
            currency=item.get("currency"),
            rating_avg=item.get("rating_avg"),
            rating_count=item.get("rating_count"),
        )

        session.add(listing)
        inserted += 1

    session.commit()
    session.close()

    print(f"Inserted {inserted} new listings for query: {query}")

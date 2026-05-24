from cmie.db import get_session_factory
from cmie.config import DEFAULT_DB_URL
from cmie.models import Listing
from cmie.connectors.tpt import TPTConnector


def ingest_tpt(query: str, page: int = 1):
    Session = get_session_factory(DEFAULT_DB_URL)
    session = Session()

    connector = TPTConnector()
    listings = connector.fetch_listings(query=query, page=page)

    inserted = 0

    for data in listings:
        existing = (
            session.query(Listing)
            .filter_by(
                marketplace=data["marketplace"],
                external_id=data["external_id"],
            )
            .first()
        )

        if existing:
            continue

        listing = Listing(**data)
        session.add(listing)
        inserted += 1

    session.commit()
    session.close()

    print(f"Inserted {inserted} new listings.")

"""
Database initialization script.
Creates initial data (sources, etc.).
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.models import Source


def init_database():
    """Initialize database with tables and seed data."""

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")

    db = SessionLocal()

    try:
        # Create initial sources
        print("Creating initial data sources...")

        sources_data = [
            {
                "name": "PagesJaunes.fr",
                "url": "https://www.pagesjaunes.fr",
                "type": "HTML",
                "robots_allowed": True,
            },
            {
                "name": "Kompass.com",
                "url": "https://fr.kompass.com",
                "type": "HTML",
                "robots_allowed": True,
            },
            {
                "name": "Societe.com",
                "url": "https://www.societe.com",
                "type": "HTML",
                "robots_allowed": True,
            },
            {
                "name": "Pappers.fr",
                "url": "https://www.pappers.fr",
                "type": "HTML",
                "robots_allowed": True,
            },
        ]

        for source_data in sources_data:
            # Check if source already exists
            existing = db.query(Source).filter(Source.url == source_data["url"]).first()

            if not existing:
                source = Source(**source_data)
                db.add(source)
                print(f"  ✅ Added source: {source_data['name']}")
            else:
                print(f"  ⏭️  Source already exists: {source_data['name']}")

        db.commit()
        print("✅ Initial data created")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    init_database()

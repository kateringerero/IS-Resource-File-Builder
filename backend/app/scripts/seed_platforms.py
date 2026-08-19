from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.platform import Platform


GORGIAS_FEATURES = {
    "tags": True,
    "ticket_fields": True,
    "macros": True,
    "views": True,
    "rules": True,
    "automations": True,
    "help_center": True,
    "flows": True,
    "chat_campaigns": True,
    "import": {
        "excel": True,
        "json": False,
        "api": True
    }
}


def seed_gorgias(db: Session) -> None:
    existing = db.query(Platform).filter(Platform.code == "gorgias").first()
    if existing:
        print("Gorgias already exists.")
        return

    platform = Platform(
        name="Gorgias",
        code="gorgias",
        features_json=GORGIAS_FEATURES,
    )
    db.add(platform)
    db.commit()
    print("Gorgias seeded successfully.")


def main():
    db = SessionLocal()
    try:
        seed_gorgias(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
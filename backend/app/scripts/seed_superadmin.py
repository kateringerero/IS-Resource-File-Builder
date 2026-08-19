from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.account import Account
from app.models.user import User


def main():
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == "isteam@admin.com").first()
        if existing_user:
            print("Superadmin already exists.")
            return

        account = db.query(Account).filter(Account.slug == "internal").first()
        if not account:
            account = Account(
                name="Internal",
                slug="internal",
                status="active",
            )
            db.add(account)
            db.commit()
            db.refresh(account)

        user = User(
            account_id=account.id,
            name="Super Admin",
            email="isteam@admin.com",
            password_hash=hash_password("isteamadmin"),
            role="superadmin",
            is_active=True,
        )
        db.add(user)
        db.commit()

        print("Superadmin seeded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
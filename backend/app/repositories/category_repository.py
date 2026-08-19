from sqlalchemy.orm import Session
from app.models.category import Category
from app.models.category_template import CategoryTemplate


def get_active_categories_by_client(db: Session, client_id: int):
    return (
        db.query(Category)
        .filter(
            Category.client_id == client_id,
            Category.is_active == True,
        )
        .all()
    )


def seed_categories_from_template(
    db: Session,
    client_id: int,
    platform_code: str,
):
    templates = (
        db.query(CategoryTemplate)
        .filter(
            CategoryTemplate.platform_code == platform_code,
            CategoryTemplate.is_active == True,
        )
        .all()
    )

    categories = []

    for t in templates:
        categories.append(
            Category(
                client_id=client_id,
                main_category=t.main_category,
                subcategory=t.subcategory,
                description=t.description,
                is_default=True,
            )
        )

    db.add_all(categories)
    db.commit()

    return categories


def format_categories_for_ai(db_categories):
    return [
        {
            "main_category": c.main_category,
            "subcategory": c.subcategory,
            "description": c.description,
        }
        for c in db_categories
    ]
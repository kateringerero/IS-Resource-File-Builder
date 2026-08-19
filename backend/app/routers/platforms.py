from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.platform import Platform
from app.models.user import User

router = APIRouter(prefix="/platforms", tags=["Platforms"])


@router.get("")
def list_platforms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    platforms = db.query(Platform).order_by(Platform.name.asc()).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "features_json": p.features_json,
        }
        for p in platforms
    ]


@router.get("/{platform_id}")
def get_platform(
    platform_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    platform = db.query(Platform).filter(Platform.id == platform_id).first()

    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")

    return {
        "id": platform.id,
        "name": platform.name,
        "code": platform.code,
        "features_json": platform.features_json,
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.client import Client
from app.models.platform import Platform
from app.models.user import User
from app.services.resource_builder import build_resource_file

router = APIRouter(prefix="/resource", tags=["Resource Builder"])


@router.get("/{client_id}")
def generate_resource(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if current_user.role != "superadmin" and client.account_id != current_user.account_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    platform = db.query(Platform).filter(Platform.id == client.platform_id).first()

    result = build_resource_file(client, platform)

    return result
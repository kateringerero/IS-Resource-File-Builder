from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.client import Client
from app.models.client_gorgias_credential import ClientGorgiasCredential
from app.schemas.gorgias_credential import ClientGorgiasCredentialUpsertRequest

router = APIRouter(prefix="/clients", tags=["Client Credentials"])

# GORGIAS
@router.post("/{client_id}/gorgias-credentials")
def upsert_client_credentials(
    client_id: int,
    payload: ClientGorgiasCredentialUpsertRequest,
    db: Session = Depends(get_db),
):
    # 1. Check client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # 2. Check if credential already exists
    credential = (
        db.query(ClientGorgiasCredential)
        .filter(ClientGorgiasCredential.client_id == client_id)
        .first()
    )

    if credential:
        # update existing
        credential.email = payload.email
        credential.api_key_encrypted = payload.api_key
        credential.api_base_url = payload.api_base_url
    else:
        # create new
        credential = ClientGorgiasCredential(
            client_id=client_id,
            email=payload.email,
            api_key_encrypted=payload.api_key,
            api_base_url=payload.api_base_url,
        )
        db.add(credential)

    db.commit()
    db.refresh(credential)

    return {
        "message": "Credentials saved successfully",
        "client_id": client_id,
    }
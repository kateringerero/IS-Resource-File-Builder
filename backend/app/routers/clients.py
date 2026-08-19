from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.client import Client
from app.models.platform import Platform
from app.models.user import User
from app.schemas.client import ClientCreateRequest, ClientUpdateRequest

router = APIRouter(prefix="/clients", tags=["Clients"])


def validate_selected_features(platform_features: dict, selected_features: dict) -> dict:
    valid_selected = {}

    for key, value in selected_features.items():
        if key not in platform_features:
            continue

        if isinstance(platform_features[key], bool):
            valid_selected[key] = bool(value) and platform_features[key]
        elif isinstance(platform_features[key], dict) and isinstance(value, dict):
            nested_valid = {}
            for nested_key, nested_value in value.items():
                if nested_key in platform_features[key]:
                    nested_valid[nested_key] = bool(nested_value) and bool(platform_features[key][nested_key])
            valid_selected[key] = nested_valid

    return valid_selected


@router.post("", status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "superadmin" and not current_user.account_id:
        raise HTTPException(status_code=400, detail="User has no account")

    platform = db.query(Platform).filter(Platform.id == payload.platform_id).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")

    account_id = current_user.account_id
    validated_features = validate_selected_features(
        platform.features_json,
        payload.selected_features_json,
    )

    client = Client(
        account_id=account_id,
        platform_id=payload.platform_id,
        name=payload.name,
        website=payload.website,
        brand_tone=payload.brand_tone,
        notes=payload.notes,
        selected_features_json=validated_features,
        status="active",
    )
    db.add(client)
    db.commit()
    db.refresh(client)

    return {
        "id": client.id,
        "name": client.name,
        "platform_id": client.platform_id,
        "website": client.website,
        "brand_tone": client.brand_tone,
        "notes": client.notes,
        "status": client.status,
        "selected_features_json": client.selected_features_json,
    }


@router.get("")
def list_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Client)

    if current_user.role != "superadmin":
        query = query.filter(Client.account_id == current_user.account_id)

    clients = query.order_by(Client.created_at.desc()).all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "platform_id": c.platform_id,
            "website": c.website,
            "brand_tone": c.brand_tone,
            "notes": c.notes,
            "status": c.status,
            "selected_features_json": c.selected_features_json,
        }
        for c in clients
    ]


@router.get("/{client_id}")
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if current_user.role != "superadmin" and client.account_id != current_user.account_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {
        "id": client.id,
        "name": client.name,
        "platform_id": client.platform_id,
        "website": client.website,
        "brand_tone": client.brand_tone,
        "notes": client.notes,
        "status": client.status,
        "selected_features_json": client.selected_features_json,
    }


@router.put("/{client_id}")
def update_client(
    client_id: int,
    payload: ClientUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if current_user.role != "superadmin" and client.account_id != current_user.account_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if payload.platform_id is not None:
        platform = db.query(Platform).filter(Platform.id == payload.platform_id).first()
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")
        client.platform_id = payload.platform_id
    else:
        platform = db.query(Platform).filter(Platform.id == client.platform_id).first()

    if payload.name is not None:
        client.name = payload.name
    if payload.website is not None:
        client.website = payload.website
    if payload.brand_tone is not None:
        client.brand_tone = payload.brand_tone
    if payload.notes is not None:
        client.notes = payload.notes
    if payload.status is not None:
        client.status = payload.status

    if payload.selected_features_json is not None and platform is not None:
        client.selected_features_json = validate_selected_features(
            platform.features_json,
            payload.selected_features_json,
        )

    db.commit()
    db.refresh(client)

    return {
        "id": client.id,
        "name": client.name,
        "platform_id": client.platform_id,
        "website": client.website,
        "brand_tone": client.brand_tone,
        "notes": client.notes,
        "status": client.status,
        "selected_features_json": client.selected_features_json,
    }
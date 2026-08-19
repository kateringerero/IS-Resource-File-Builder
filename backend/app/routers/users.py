from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_superadmin
from app.core.security import hash_password
from app.models.account import Account
from app.models.user import User
from app.schemas.user_management import UserCreateRequest, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users"])

# Create User
@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    # Validate account exists
    account = None
    if request.account_id:
        account = db.query(Account).filter(Account.id == request.account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

    # Email unique validation
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash password
    hashed = hash_password(request.password)

    user = User(
        account_id=request.account_id,
        name=request.name,
        email=request.email,
        password=hashed,
        role=request.role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# Get User
@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# List Users
@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    users = db.query(User).all()
    return users

# Update User
@router.put("/{user_id}")
def update_user(
    user_id: int,
    request: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if request.account_id:
        account = db.query(Account).filter(Account.id == request.account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        user.account_id = request.account_id

    if request.name:
        user.name = request.name

    if request.email:
        # Prevent duplicate email
        if db.query(User).filter(User.email == request.email, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = request.email

    if request.password:
        user.password = hash_password(request.password)

    if request.role:
        user.role = request.role

    if request.is_active is not None:
        user.is_active = request.is_active

    db.commit()
    db.refresh(user)

    return user

# Delete User
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

# Disable User
@router.post("/{user_id}/disable")
def disable_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return {"message": "User disabled", "user_id": user_id}


# Enable User
@router.post("/{user_id}/enable")
def enable_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()

    return {"message": "User enabled", "user_id": user_id} 

# Update user / assign role
@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.role is not None:
        if payload.role not in {"superadmin", "admin", "user"}:
            raise HTTPException(status_code=400, detail="Invalid role")
        user.role = payload.role

        if payload.role == "superadmin":
            user.account_id = None

    if payload.account_id is not None:
        account = db.query(Account).filter(Account.id == payload.account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        user.account_id = payload.account_id

    if payload.name is not None:
        user.name = payload.name

    if payload.email is not None:
        existing_email = (
            db.query(User)
            .filter(User.email == payload.email, User.id != user_id)
            .first()
        )
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = payload.email

    if payload.password is not None:
        user.password_hash = hash_password(payload.password)

    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "account_id": user.account_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }
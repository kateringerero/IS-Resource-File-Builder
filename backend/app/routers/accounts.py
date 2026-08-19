from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_superadmin
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreateRequest, AccountUpdateRequest

router = APIRouter(prefix="/accounts", tags=["Accounts"])

# Create Account
@router.post("", status_code=status.HTTP_201_CREATED)
def create_account(
    request: AccountCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    account = Account(
        name=request.name,
        slug=request.slug,
        status="active",
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account

# Get Account
@router.get("/{account_id}")
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# List accounts
@router.get("/")
def get_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    accounts = db.query(Account).all()
    return accounts

# Update / disable account
@router.put("/{account_id}")
def update_account(
    account_id: int,
    request: AccountUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if request.name:
        account.name = request.name
    if request.slug:
        account.slug = request.slug
    if request.status:
        account.status = request.status

    db.commit()
    db.refresh(account)

    return account

# Delete account
@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)
    db.commit()

    return {"message": "Account deleted successfully"}

# Dedicated Disable endpoint
@router.post("/{account_id}/disable")
def disable_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.status = "inactive"
    db.commit()

    return {"message": "Account disabled", "account_id": account_id}

# Dedicated Enable endpoint
@router.post("/{account_id}/enable")
def enable_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.status = "active"
    db.commit()

    return {"message": "Account enabled", "account_id": account_id} 
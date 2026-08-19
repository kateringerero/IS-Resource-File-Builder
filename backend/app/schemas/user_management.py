from pydantic import BaseModel, EmailStr


class UserCreateRequest(BaseModel):
    account_id: int | None = None
    name: str
    email: EmailStr
    password: str
    role: str  # superadmin | admin | user


class UserUpdateRequest(BaseModel):
    account_id: int | None = None
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None
    is_active: bool | None = None
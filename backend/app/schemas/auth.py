from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserMeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    account_id: int | None
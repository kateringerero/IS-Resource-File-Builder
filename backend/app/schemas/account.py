from pydantic import BaseModel


class AccountCreateRequest(BaseModel):
    name: str
    slug: str


class AccountUpdateRequest(BaseModel):
    name: str | None = None
    slug: str | None = None
    status: str | None = None
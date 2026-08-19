from pydantic import BaseModel


class ClientGorgiasCredentialUpsertRequest(BaseModel):
    email: str
    api_key: str
    api_base_url: str
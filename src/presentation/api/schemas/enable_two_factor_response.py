from pydantic import BaseModel


class EnableTwoFactorResponse(BaseModel):
    secret: str
    provisioning_uri: str

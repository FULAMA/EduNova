from pydantic import BaseModel


class VerifyLoginTwoFactorResponse(BaseModel):
    authenticated: bool
    access_token: str
    refresh_token: str

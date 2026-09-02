from pydantic import BaseModel


class RefreshAccessTokenResponse(BaseModel):
    authenticated: bool
    access_token: str
    refresh_token: str

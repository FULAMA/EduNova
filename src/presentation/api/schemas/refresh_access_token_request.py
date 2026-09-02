from pydantic import BaseModel, Field


class RefreshAccessTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)

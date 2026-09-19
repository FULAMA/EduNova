from pydantic import BaseModel, ConfigDict, Field


class RefreshAccessTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(min_length=1)

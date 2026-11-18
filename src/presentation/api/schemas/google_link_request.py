from pydantic import BaseModel, ConfigDict, Field


class GoogleLinkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_token: str = Field(min_length=1)
    nonce: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=1, max_length=256)
    totp_code: str | None = Field(default=None, min_length=6, max_length=6)

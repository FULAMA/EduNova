from pydantic import BaseModel, ConfigDict, Field


class GoogleLinkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_token: str = Field(min_length=1)

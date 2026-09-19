from pydantic import BaseModel, ConfigDict, Field


class VerifyTwoFactorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )

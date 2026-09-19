from pydantic import BaseModel, ConfigDict, Field


class VerifyLoginTwoFactorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    two_factor_token: str = Field(min_length=1)
    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )

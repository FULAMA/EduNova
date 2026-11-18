from pydantic import BaseModel, ConfigDict, Field


class RegisterEstablishmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    school_name: str = Field(min_length=2, max_length=200)
    admin_name: str = Field(min_length=2, max_length=150)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)

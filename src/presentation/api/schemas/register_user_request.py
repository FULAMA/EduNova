from pydantic import BaseModel, ConfigDict, Field


class RegisterUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3)
    password: str = Field(min_length=8)
    role: str = Field(min_length=1)

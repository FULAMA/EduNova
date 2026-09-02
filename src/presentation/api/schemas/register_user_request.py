from pydantic import BaseModel, Field


class RegisterUserRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)
    role: str = Field(min_length=1)

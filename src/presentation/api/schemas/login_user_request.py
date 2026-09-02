from pydantic import BaseModel, Field


class LoginUserRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)

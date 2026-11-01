from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SchoolProfileInput(BaseModel):
    legal_name: str = Field(min_length=1, max_length=200)
    display_name: str = Field(min_length=1, max_length=160)
    address: str | None = Field(default=None, max_length=300)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=254)
    website: str | None = Field(default=None, max_length=255)
    logo_url: str | None = Field(default=None, max_length=500)

    @field_validator("*", mode="before")
    @classmethod
    def trim_strings(cls, value: object) -> object:
        return value.strip() or None if isinstance(value, str) else value


class SchoolProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID
    legal_name: str
    display_name: str
    address: str | None
    phone: str | None
    email: str | None
    website: str | None
    logo_url: str | None

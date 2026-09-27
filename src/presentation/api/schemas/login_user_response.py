from pydantic import BaseModel


class LoginUserResponse(BaseModel):
    authenticated: bool
    two_factor_required: bool
    two_factor_token: str | None
    access_token: str | None
    refresh_token: str | None

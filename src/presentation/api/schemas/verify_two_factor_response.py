from pydantic import BaseModel


class VerifyTwoFactorResponse(BaseModel):
    verified: bool

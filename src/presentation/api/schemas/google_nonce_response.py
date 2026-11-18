from pydantic import BaseModel


class GoogleNonceResponse(BaseModel):
    nonce: str

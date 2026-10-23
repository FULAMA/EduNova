from pydantic import BaseModel


class GoogleLinkResponse(BaseModel):
    linked: bool

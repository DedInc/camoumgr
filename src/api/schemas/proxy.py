from pydantic import BaseModel


class ProxyCheckRequest(BaseModel):
    proxy: str
    timeout: int | None = None


class ProxyCheckResponse(BaseModel):
    success: bool
    message: str

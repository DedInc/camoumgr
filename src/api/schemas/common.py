from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "OK"


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    field: str | None = None

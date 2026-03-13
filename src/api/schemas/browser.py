from pydantic import BaseModel


class BrowserStatusResponse(BaseModel):
    name: str
    is_running: bool


class RunningBrowsersResponse(BaseModel):
    running: list[str]
    count: int


class LaunchResponse(BaseModel):
    success: bool
    message: str

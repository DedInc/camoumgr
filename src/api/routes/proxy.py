from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from ..dependencies import get_proxy_service
from ..schemas.proxy import ProxyCheckRequest, ProxyCheckResponse

if TYPE_CHECKING:
    from ...interfaces import IProxyService

router = APIRouter(prefix="/proxy", tags=["proxy"])


@router.post("/check", response_model=ProxyCheckResponse)
def check_proxy(
    body: ProxyCheckRequest,
    ps: IProxyService = Depends(get_proxy_service),
) -> ProxyCheckResponse:
    ok, message = ps.check_proxy_sync(body.proxy, body.timeout or 10)
    return ProxyCheckResponse(success=ok, message=message)

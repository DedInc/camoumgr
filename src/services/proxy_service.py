from ..config import PROXY_CHECK_TIMEOUT
from ..utils.proxy_checker import check_proxy_sync as _check_sync


class ProxyService:
    def __init__(self, default_timeout: int = PROXY_CHECK_TIMEOUT) -> None:
        self._default_timeout = default_timeout

    def check_proxy_sync(
        self,
        proxy_str: str,
        timeout: int | None = None,
    ) -> tuple[bool, str]:
        return _check_sync(proxy_str, timeout or self._default_timeout)

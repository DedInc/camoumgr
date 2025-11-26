import asyncio
from typing import Tuple

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from .proxy_parser import parse_proxy


async def check_proxy(proxy_str: str, timeout: int = 10) -> Tuple[bool, str]:
    if not AIOHTTP_AVAILABLE:
        return True, "Proxy check skipped (aiohttp not installed)"
    
    proxy_config = parse_proxy(proxy_str)
    if not proxy_config:
        return False, "Invalid proxy format"
    
    proxy_url = proxy_config["server"]
    if "username" in proxy_config:
        scheme, rest = proxy_url.split("://", 1)
        proxy_url = f"{scheme}://{proxy_config['username']}:{proxy_config.get('password', '')}@{rest}"
    
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.get(
                "https://httpbin.org/ip",
                proxy=proxy_url
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return True, f"Proxy working. IP: {data.get('origin', 'unknown')}"
                else:
                    return False, f"Proxy returned status {response.status}"
    except asyncio.TimeoutError:
        return False, "Proxy connection timed out"
    except aiohttp.ClientProxyConnectionError:
        return False, "Failed to connect to proxy"
    except aiohttp.ClientError as e:
        return False, f"Proxy error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def check_proxy_sync(proxy_str: str, timeout: int = 10) -> Tuple[bool, str]:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(check_proxy(proxy_str, timeout))
        finally:
            loop.close()
    except Exception as e:
        return False, f"Error checking proxy: {str(e)}"

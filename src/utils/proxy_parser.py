from typing import Optional, Dict
from urllib.parse import urlparse


def parse_proxy(proxy_str: str) -> Optional[Dict]:
    if not proxy_str or proxy_str == "None":
        return None
    try:
        if "://" not in proxy_str:
            proxy_str = "http://" + proxy_str
        p = urlparse(proxy_str)
        if not p.hostname or not p.port:
            return None
        cfg = {"server": f"{p.scheme}://{p.hostname}:{p.port}"}
        if p.username:
            cfg["username"] = p.username
        if p.password:
            cfg["password"] = p.password
        return cfg
    except Exception:
        return None

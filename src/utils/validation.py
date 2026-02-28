import re

_INVALID_CHARS = '<>:"/\\|?*'
_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
_PROXY_PATTERN = re.compile(
    r"^(?:(?P<scheme>https?|socks[45])://)?"
    r"(?:(?P<user>[^:@]+):(?P<pass>[^@]+)@)?"
    r"(?P<host>[a-zA-Z0-9.-]+|\d{1,3}(?:\.\d{1,3}){3})"
    r":(?P<port>\d{1,5})$",
)


def validate_profile_name(name: str) -> tuple[bool, str]:
    if not name:
        return False, "Profile name cannot be empty"

    if len(name) > 64:
        return False, "Profile name must be 64 characters or less"

    found_invalid = [c for c in name if c in _INVALID_CHARS]
    if found_invalid:
        return False, f"Name contains invalid characters: {', '.join(found_invalid)}"

    if name != name.strip():
        return False, "Name cannot start or end with spaces"

    if name.upper() in _RESERVED_NAMES:
        return False, f"'{name}' is a reserved system name"

    return True, ""


def validate_proxy_format(proxy_str: str) -> tuple[bool, str]:
    if not proxy_str:
        return True, ""

    match = _PROXY_PATTERN.match(proxy_str)
    if not match:
        return False, "Invalid proxy format. Use: [scheme://][user:pass@]host:port"

    port = int(match.group("port"))
    if not 1 <= port <= 65535:
        return False, f"Port must be between 1 and 65535, got {port}"

    return True, ""

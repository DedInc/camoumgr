import re
from typing import Tuple


def validate_profile_name(name: str) -> Tuple[bool, str]:
    if not name:
        return False, "Profile name cannot be empty"
    
    if len(name) > 64:
        return False, "Profile name must be 64 characters or less"
    
    invalid_chars = '<>:"/\\|?*'
    found_invalid = [c for c in name if c in invalid_chars]
    if found_invalid:
        return False, f"Name contains invalid characters: {', '.join(found_invalid)}"
    
    if name.startswith(' ') or name.endswith(' '):
        return False, "Name cannot start or end with spaces"
    
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 
                      'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                      'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    if name.upper() in reserved_names:
        return False, f"'{name}' is a reserved system name"
    
    return True, ""


def validate_proxy_format(proxy_str: str) -> Tuple[bool, str]:
    if not proxy_str:
        return True, ""
    
    proxy_pattern = re.compile(
        r'^(?:(?P<scheme>https?|socks[45])://)?'
        r'(?:(?P<user>[^:@]+):(?P<pass>[^@]+)@)?'
        r'(?P<host>[a-zA-Z0-9.-]+|\d{1,3}(?:\.\d{1,3}){3})'
        r':(?P<port>\d{1,5})$'
    )
    
    match = proxy_pattern.match(proxy_str)
    if not match:
        return False, "Invalid proxy format. Use: [scheme://][user:pass@]host:port"
    
    port = int(match.group('port'))
    if port < 1 or port > 65535:
        return False, f"Port must be between 1 and 65535, got {port}"
    
    return True, ""

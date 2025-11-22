from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Profile:
    name: str
    proxy: Optional[str] = None
    os_type: str = "windows"
    
    def to_dict(self):
        return asdict(self)

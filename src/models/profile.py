from dataclasses import asdict, dataclass


@dataclass
class Profile:
    name: str
    proxy: str | None = None
    os_type: str = "windows"

    def to_dict(self):
        return asdict(self)

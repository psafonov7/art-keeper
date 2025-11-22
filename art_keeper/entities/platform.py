from enum import Enum


class Platform(Enum):
    Linux = ["linux"]
    Windows = ["windows", "win"]
    Mac = ["darwin", "macos", "mac-os", "mac"]

    @classmethod
    def from_string(cls, string: str) -> "Platform":
        string = string.lower()
        for member in cls:
            if string in member.value:
                return member
        raise ValueError(f"Arch {string} doesn't exists")

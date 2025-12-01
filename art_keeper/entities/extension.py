from enum import Enum


class FileExtension(Enum):
    Exe = [".exe", "exe"]
    Deb = [".deb", "deb"]

    @classmethod
    def from_string(cls, string: str) -> "FileExtension":
        string = string.lower()
        for member in cls:
            if string in member.value:
                return member
        raise ValueError(f"Arch {string} doesn't exists")

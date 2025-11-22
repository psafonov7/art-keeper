from enum import Enum


class Arch(Enum):
    X86_64 = ["x86_64", "x86-64", "amd64"]
    ARM64 = ["arm64"]

    @classmethod
    def from_string(cls, string: str) -> "Arch":
        string = string.lower()
        for member in cls:
            if string in member.value:
                return member
        raise ValueError(f"Arch {string} doesn't exists")

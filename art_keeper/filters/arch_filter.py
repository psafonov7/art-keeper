from art_keeper.entities.arch import Arch

from .filter import Filter


class ArchFilter(Filter):
    def __init__(self, name: str):
        self._arch = Arch.from_string(name)

    def is_pass(self, name: str) -> bool:
        for arch in self._arch.value:
            if arch in name:
                return True
        return False

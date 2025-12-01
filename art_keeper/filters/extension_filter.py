from art_keeper.entities.extension import FileExtension

from .filter import Filter


class ExtensionFilter(Filter):
    def __init__(self, name: str):
        self._extension = FileExtension.from_string(name)

    def is_pass(self, name: str) -> bool:
        for ext in self._extension.value:
            if ext in name:
                return True
        return False

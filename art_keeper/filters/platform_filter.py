from art_keeper.entities.platform import Platform

from .filter import Filter


class PlatformFilter(Filter):
    def __init__(self, name: str):
        self._platform = Platform.from_string(name)

    def is_pass(self, name: str) -> bool:
        for platform in self._platform.value:
            if platform in name:
                return True
        return False

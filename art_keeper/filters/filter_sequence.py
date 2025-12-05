from art_keeper.config import ConfigFilter

from .arch_filter import ArchFilter
from .filter import Filter
from .platform_filter import PlatformFilter
from .extension_filter import ExtensionFilter
from .regex_filter import RegExFilter

class FilterSequence:
    def __init__(self, configs: list[ConfigFilter]):
        self._filters: list[Filter] = []
        for config in configs:
            filter = self._filter_from_config(config)
            self._filters.append(filter)

    def is_pass(self, name: str) -> bool:
        for f in self._filters:
            if not f.is_pass(name):
                return False
        return True

    def _filter_from_config(self, config: ConfigFilter) -> Filter:
        match config.type:
            case "arch":
                return ArchFilter(config.value)
            case "platform":
                return PlatformFilter(config.value)
            case "extension":
                return ExtensionFilter(config.value)
            case "regex":
                return RegExFilter(config.value)
            case _:
                raise ValueError(f"Filter with type {config.type} doesn't exists")

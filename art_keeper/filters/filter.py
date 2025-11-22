from abc import ABC, abstractmethod


class Filter(ABC):
    @abstractmethod
    def is_pass(self, name: str) -> bool:
        pass

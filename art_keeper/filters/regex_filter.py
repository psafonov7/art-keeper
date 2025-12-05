import re

from .filter import Filter


class RegExFilter(Filter):
    def __init__(self, regex: str):
        self.regex = regex

    def is_pass(self, name: str) -> bool:
        rf = rf"{self.regex}"
        match = re.search(rf, name)
        return match is not None

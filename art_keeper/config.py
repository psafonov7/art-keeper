from serde import serde


@serde
class ConfigFilter:
    type: str
    value: str


@serde
class Config:
    repos: list[str]
    filters: list[ConfigFilter]

from typing import Optional

from serde import serde


@serde
class ConfigFilter:
    type: str
    value: str


@serde
class ConfigRepo:
    name: str
    filters: Optional[list[ConfigFilter]]
    last_releases_count: Optional[int]
    verify_checksums: bool = True


@serde
class Config:
    repos: list[ConfigRepo]

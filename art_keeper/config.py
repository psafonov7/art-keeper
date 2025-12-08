from typing import Optional

from serde import serde


@serde
class ConfigFilter:
    type: str
    value: str


@serde
class ConfigArtifactsRepo:
    name: str
    filters: Optional[list[ConfigFilter]]
    last_releases_count: Optional[int]
    verify_checksums: bool = True


@serde
class ConfigMirrorRepo:
    source_url: str
    target_url: str


@serde
class Config:
    artifacts: list[ConfigArtifactsRepo]
    repos: list[ConfigMirrorRepo]

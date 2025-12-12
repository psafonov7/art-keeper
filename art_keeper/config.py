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
class ConfigRepo:
    url: str
    platform: str = "github"
    api_endpoint: Optional[str] = None
    ssl: bool = True


@serde
class ConfigMirrorRepo:
    source: ConfigRepo
    targets: list[ConfigRepo]


@serde
class Config:
    artifacts: list[ConfigArtifactsRepo]
    repos: list[ConfigMirrorRepo]

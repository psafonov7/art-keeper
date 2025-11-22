import requests
from serde import serde
from serde.json import from_json


@serde
class Asset:
    browser_download_url: str
    name: str
    size: int


@serde
class Release:
    url: str
    tag_name: str
    published_at: str
    assets: list[Asset]


class GithubClient:
    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        self._token = token
        self._base_url = base_url

    def get_releases(self, repo: str) -> list[Release]:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._token}",
        }
        url = f"{self._base_url}/repos/{repo}/releases"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return from_json(list[Release], response.text)

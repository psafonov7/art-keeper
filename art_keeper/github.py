import aiohttp
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

    async def get_releases(self, repo: str) -> list[Release]:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._token}",
        }
        url = f"{self._base_url}/repos/{repo}/releases"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                text = await response.text()
                return from_json(list[Release], text)

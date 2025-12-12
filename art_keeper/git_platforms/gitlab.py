import urllib.parse

import aiohttp

from .git_platform import GitPlatform


class Gitlab(GitPlatform):
    def __init__(self, api_url: str, token: str, ssl: bool = True):
        self._api_url = api_url
        self._token = token
        self._ssl = ssl
        self._auth_header = {"Authorization": f"Bearer {self._token}"}

    async def prepare_repo(self, repo_path: str):
        async with aiohttp.ClientSession() as session:
            if not await self.is_repo_exists(repo_path, session):
                repo_name = repo_path.split("/")[1]
                success = await self.create_repo(repo_name, session)
                if not success:
                    raise ValueError(f"Can't create repo '{repo_name}'")

    async def is_repo_exists(
        self, repo_path: str, session: aiohttp.ClientSession
    ) -> bool:
        repo_path_encoded = urllib.parse.quote(repo_path, "")
        url = f"{self._api_url}/projects/{repo_path_encoded}"
        async with session.get(
            url, headers=self._auth_header, ssl=self._ssl
        ) as response:
            return response.ok

    async def create_repo(self, repo_name: str, session: aiohttp.ClientSession) -> bool:
        url = f"{self._api_url}/projects"
        body = {
            "name": repo_name,
            "visibility": "private",
        }
        async with session.post(
            url, headers=self._auth_header, json=body, ssl=self._ssl
        ) as response:
            return response.ok

import aiohttp

from .git_platform import GitPlatform


class Forgejo(GitPlatform):
    def __init__(
        self, api_url: str, token: str, api_version: str = "v1", ssl: bool = True
    ):
        self._api_url = api_url
        self._token = token
        self._auth_header = {"Authorization": f"Bearer {self._token}"}
        self._ssl = ssl

    async def prepare_repo(self, repo_path: str):
        async with aiohttp.ClientSession() as session:
            if not await self.is_repo_exists(repo_path, session):
                repo_name = repo_path.split("/")[1]
                result = await self.create_repo(repo_name, session)
                if not result:
                    raise ValueError(f"Can't create repo '{repo_name}'")
                disabled_actions = await self.disable_actions(repo_path, session)
                if not disabled_actions:
                    raise ValueError(f"Can't disable actions in {repo_name}'")

    async def is_repo_exists(
        self, repo_path: str, session: aiohttp.ClientSession
    ) -> bool:
        url = f"{self._api_url}/repos/{repo_path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=self._auth_header, ssl=self._ssl
            ) as response:
                return response.ok

    async def create_repo(self, repo_name: str, session: aiohttp.ClientSession) -> bool:
        url = f"{self._api_url}/user/repos"
        body = {
            "name": repo_name,
            "private": True,
            "auto_init": False,
        }
        async with session.post(
            url, headers=self._auth_header, json=body, ssl=self._ssl
        ) as response:
            return response.ok

    async def disable_actions(
        self, repo_path: str, session: aiohttp.ClientSession
    ) -> bool:
        url = f"{self._api_url}/repos/{repo_path}"
        body = {"has_actions": False}
        async with session.patch(
            url, headers=self._auth_header, json=body, ssl=self._ssl
        ) as response:
            return response.ok

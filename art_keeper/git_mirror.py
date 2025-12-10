import shutil

from .config import ConfigMirrorRepo, ConfigRepo
from .git import Git
from .git_platforms.forgejo import Forgejo
from .utils import create_dir, getenv


class GitMirror:
    def __init__(self, workdir: str):
        self._workdir = workdir
        self._git = Git(self._workdir)

    async def mirror_repos(self, repos: list[ConfigMirrorRepo]):
        for repo in repos:
            await self.mirror_repo(repo.source, repo.target)

    async def mirror_repo(self, source_repo: ConfigRepo, target_repo: ConfigRepo):
        source_repo_path = self._git.get_repo_path_from_url(source_repo.url)
        repo_name = source_repo_path.split("/")[1]
        repo_dir = self._workdir + "/" + repo_name
        # create_dir(repo_dir)
        await self._mirror_repo(source_repo.url, repo_dir)

        platform = self._get_git_platform(target_repo)
        target_repo_path = self._git.get_repo_path_from_url(target_repo.url)
        await platform.prepare_repo(target_repo_path)

        await self._push_mirror(target_repo.url, repo_dir)

        # shutil.rmtree(repo_dir)

    def _get_git_platform(self, config: ConfigRepo) -> Forgejo:
        if not config.api_endpoint:
            raise ValueError(f"API endpoint is missing for '{config.platform}'")
        match config.platform:
            case "forgejo":
                return Forgejo(
                    api_url=config.api_endpoint,
                    token=getenv("FORGEJO_TOKEN"),
                    ssl=config.ssl,
                )
            case _:
                raise ValueError(f"There is no platform '{config.platform}'")

    async def _mirror_repo(self, source_url: str, repo_dir: str):
        self._git.add_to_known_hosts_url(source_url)
        mirror_result = await self._git.git_mirror_repo(source_url, repo_dir)
        if not mirror_result.success:
            raise ValueError(f"Can't mirror repo: {mirror_result.stderr}")

    async def _push_mirror(self, target_url: str, repo_dir: str):
        self._git.add_to_known_hosts_url(target_url)
        push_result = await self._git.git_push_mirror(repo_dir, target_url)
        if not push_result.success:
            raise ValueError(f"Can't push repo: {push_result.stderr}")

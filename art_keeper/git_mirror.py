from .config import ConfigMirrorRepo, ConfigRepo
from .git import Git
from .git_platforms.forgejo import Forgejo
from .git_platforms.git_platform import GitPlatform
from .git_platforms.gitlab import Gitlab
from .utils import getenv


class GitMirror:
    def __init__(self, workdir: str):
        self._workdir = workdir
        self._git = Git(self._workdir)

    async def mirror_repos(self, repos: list[ConfigMirrorRepo]):
        for repo in repos:
            await self.mirror_repo(repo.source, repo.targets)

    async def mirror_repo(
        self, source_repo: ConfigRepo, target_repos: list[ConfigRepo]
    ):
        source_repo_path = self._git.get_repo_path_from_url(source_repo.url)
        repo_name = source_repo_path.split("/")[1]
        repo_dir = self._workdir + "/" + repo_name
        # create_dir(repo_dir)
        await self._mirror_repo(source_repo.url, repo_dir)

        for repo in target_repos:
            platform = self._get_git_platform(repo)
            path = self._git.get_repo_path_from_url(repo.url)
            await platform.prepare_repo(path)
            await self._push_mirror(repo.url, repo_dir)

        # shutil.rmtree(repo_dir)

    def _get_git_platform(self, config: ConfigRepo) -> GitPlatform:
        if not config.api_endpoint:
            raise ValueError(f"API endpoint is missing for '{config.platform}'")
        match config.platform:
            case "forgejo":
                return Forgejo(
                    api_url=config.api_endpoint,
                    token=getenv("FORGEJO_TOKEN"),
                    ssl=config.ssl,
                )
            case "gitlab":
                return Gitlab(
                    api_url=config.api_endpoint,
                    token=getenv("GITLAB_TOKEN"),
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
        success = await self._git.git_push_mirror(repo_dir, target_url)
        if not success:
            raise ValueError(f"Can't push repo '{repo_dir}' to '{target_url}'")

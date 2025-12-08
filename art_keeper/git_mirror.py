import os
from pathlib import Path

from .cmd import CmdResult, run_cmd, run_cmd_sync
from .utils import get_substring_between_strings


class GitMirror:
    def __init__(self, workdir: str | Path):
        self.workdir = workdir

    async def sync_repo(self, repo_name: str, source_url: str, target_url: str):
        repo_dir = str(self.workdir) + "/" + repo_name
        await self._mirror_repo(source_url, repo_dir)
        await self._push_mirror(target_url, repo_dir)

    async def _mirror_repo(self, source_url: str, repo_dir: str):
        self._add_to_known_hosts_url(source_url)
        mirror_result = await self._git_mirror_repo(source_url, repo_dir)
        if not mirror_result.success:
            raise ValueError(f"Can't mirror repo: {mirror_result.stderr}")

    async def _git_mirror_repo(self, source_url: str, repo_path: str) -> CmdResult:
        mirror_path = Path(repo_path)
        if mirror_path.exists():
            return await run_cmd(["git", "remote", "update"], mirror_path)
        else:
            cmd = ["git", "clone", "--mirror", source_url, mirror_path]
            return await run_cmd(cmd, self.workdir)

    async def _push_mirror(self, target_url: str, repo_dir: str):
        self._add_to_known_hosts_url(target_url)
        push_result = await self._git_push_mirror(repo_dir, target_url)
        if not push_result.success:
            raise ValueError(f"Can't push repo: {push_result.stderr}")

    async def _git_push_mirror(self, repo_path: str, target_url: str) -> CmdResult:
        result = await run_cmd(
            ["git", "remote", "add", "target", target_url],
            workdir=repo_path,
        )
        if not result.success:
            return result
        return await run_cmd(
            ["git", "push", "target", "--mirror"],
            workdir=repo_path,
        )

    def _add_to_known_hosts_url(self, url: str):
        if not url.startswith("ssh://"):
            return
        host, port = self._host_and_port_from_url(url)
        print(url, host, port)
        add_result = self._add_to_known_hosts(host, port)
        if not add_result:
            raise ValueError(f"Can't add host '{host} to known_hosts'")

    def _add_to_known_hosts(self, host: str, port: int | None = None) -> bool:
        known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
        cmd = ["ssh-keyscan"]
        if port:
            cmd += ["-p", str(port)]
        cmd.append(host)
        result = run_cmd_sync(cmd)
        if result.success:
            with open(known_hosts_path, "a") as f:
                f.write(result.stdout)
            return True
        return False

    def _host_and_port_from_url(self, url: str) -> tuple[str, int | None]:
        host_with_port = get_substring_between_strings(url, "git@", "/")
        if not host_with_port:
            raise ValueError(f"Can't find host and port in URL: {url}")
        if ":" in host_with_port:
            parts = host_with_port.split(":")
            return (parts[0], int(parts[1]))
        else:
            return (host_with_port, None)

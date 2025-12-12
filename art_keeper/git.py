import os
import re
from pathlib import Path

from .cmd import CmdResult, run_cmd, run_cmd_sync
from .utils import get_substring_between_strings, safe_cast


class Git:
    def __init__(self, workdir: str):
        self._workdir = workdir

    async def git_mirror_repo(self, source_url: str, repo_path: str) -> CmdResult:
        mirror_path = Path(repo_path)
        if mirror_path.exists():
            return await run_cmd(["git", "remote", "update"], mirror_path)
        else:
            cmd = ["git", "clone", "--mirror", source_url, repo_path]
            return await run_cmd(cmd)

    async def git_push_mirror(self, repo_path: str, target_url: str) -> bool:
        success = await self.add_remote("target", target_url, repo_path)
        if not success:
            return False
        return await self.push("target", repo_path, True)

    async def push(
        self, remote_name: str, repo_path: str, with_tags: bool = False
    ) -> bool:
        result = await run_cmd(
            ["git", "push", remote_name, "--all"],
            workdir=repo_path,
        )
        if not with_tags:
            return result.success
        result = await run_cmd(
            ["git", "push", remote_name, "--tags"],
            workdir=repo_path,
        )
        return result.success

    async def add_remote(self, name: str, url: str, repo_path: str) -> bool:
        existing = await self.get_remote_url(name, repo_path)
        if existing:
            if existing == url:
                return True
            else:
                await self.remote_remove(name, repo_path)
                await self.remote_prune(name, repo_path)
        result = await run_cmd(
            ["git", "remote", "add", name, url],
            workdir=repo_path,
        )
        return result.success

    async def remote_remove(self, name: str, repo_path: str) -> bool:
        result = await run_cmd(
            ["git", "remote", "remove", name],
            workdir=repo_path,
        )
        return result.success

    async def remote_prune(self, name: str, repo_path: str) -> bool:
        result = await run_cmd(
            ["git", "remote", "prune", name],
            workdir=repo_path,
        )
        return result.success

    async def get_remote_url(self, name: str, repo_path: str) -> str | None:
        result = await run_cmd(
            ["git", "remote", "get-url", name],
            workdir=repo_path,
        )
        if not result.success:
            return None
        return result.stdout

    def add_to_known_hosts_url(self, url: str):
        if url.startswith("http"):
            return
        host, port = self.host_and_port_from_url(url)
        success = self.add_to_known_hosts(host, port)
        if not success:
            raise ValueError(f"Can't add host '{host}' to known_hosts")

    def add_to_known_hosts(self, host: str, port: int | None = None) -> bool:
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

    def host_and_port_from_url(self, url: str) -> tuple[str, int | None]:
        host_with_port = get_substring_between_strings(url, "git@", "/")
        if not host_with_port:
            raise ValueError(f"Can't find host and port in URL: {url}")
        if ":" in host_with_port:
            parts = host_with_port.split(":")
            return (parts[0], safe_cast(parts[1], int))
        else:
            return (host_with_port, None)

    def get_repo_path_from_url(self, url: str) -> str:
        url = re.sub(r"\.git$", "", url)
        ssh_match = re.match(r"ssh:\/\/git@([^:]+):?([0-9]*)\/(.*)", url)
        if ssh_match:
            return ssh_match.group(3)
        https_match = re.match(r"https?://[^/]+/(.+)", url)
        if https_match:
            return https_match.group(1)
        git_match = re.match(r"git@[^:]+:?(.*\/.*)", url)
        if git_match:
            return git_match.group(1)
        raise ValueError(f"Unable to get repo name from URL: {url}")

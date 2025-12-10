import os
import re
from pathlib import Path

from .cmd import CmdResult, run_cmd, run_cmd_sync
from .utils import get_substring_between_strings


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

    async def git_push_mirror(self, repo_path: str, target_url: str) -> CmdResult:
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

    def add_to_known_hosts_url(self, url: str):
        if not url.startswith("ssh://"):
            return
        host, port = self.host_and_port_from_url(url)
        print(url, host, port)
        add_result = self.add_to_known_hosts(host, port)
        if not add_result:
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
            return (parts[0], int(parts[1]))
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
        git_match = re.match(r"git://[^/]+/(.+)", url)
        if git_match:
            return git_match.group(1)
        raise ValueError(f"Unable to get repo name from URL: {url}")

import asyncio
import subprocess
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class CmdResult:
    success: bool
    stdout: str
    stderr: str
    returncode: int

    @property
    def output(self) -> str:
        return self.stdout.strip()

    def raise_if_error(self):
        if not self.success:
            raise RuntimeError(f"Git command failed:\n{self.stderr}")


async def run_cmd(
    cmd: list[str], workdir: str | Path = ".", input: Optional[str] = None
) -> CmdResult:
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        partial(run_cmd_sync, cmd=cmd, workdir=workdir, input=input),
    )
    return result


def run_cmd_sync(
    cmd: list[str], workdir: str | Path = ".", input: Optional[str] = None
) -> CmdResult:
    try:
        proc = subprocess.run(
            cmd,
            cwd=workdir,
            input=input,
            text=True,
            capture_output=True,
            timeout=30,
        )
        return CmdResult(
            success=proc.returncode == 0,
            stdout=proc.stdout,
            stderr=proc.stderr,
            returncode=proc.returncode,
        )
    except Exception as e:
        return CmdResult(
            success=False,
            stdout="",
            stderr=str(e),
            returncode=-1,
        )

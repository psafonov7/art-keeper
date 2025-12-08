import asyncio
import re
import shutil

from dotenv import load_dotenv
from serde.yaml import from_yaml

from .config import Config
from .git_mirror import GitMirror
from .mover import Mover
from .utils import create_dir, get_substring_between_strings, getenv

CONFIG_FILE_NAME = "config.yaml"
ARTIFACTS_FOLDER_NAME = "artifacts"


async def main():
    load_dotenv()
    data_dir = getenv("DATA_DIR")
    config_file_path = f"{data_dir}/{CONFIG_FILE_NAME}"
    config = load_config(config_file_path)
    # artifacts_folder_path = f"{data_dir}/{ARTIFACTS_FOLDER_NAME}"
    # dry_run = getenv_bool("DRY_RUN")

    # mover = Mover(
    #     config=config,
    #     artifacts_path=artifacts_folder_path,
    #     dry_run=dry_run,
    # )
    # await mover.move_all()

    for repo in config.repos:
        await mirror_repo(repo.source_url, repo.target_url, data_dir)


async def mirror_repo(source_url: str, target_url: str, data_dir: str):
    mirrors_dir = data_dir + "/" + "repos"
    create_dir(mirrors_dir)
    mirror = GitMirror(mirrors_dir)
    full_repo_name = get_full_repo_name_from_url(source_url)
    name = full_repo_name.split("/")[1]
    await mirror.sync_repo(
        repo_name=name,
        source_url=source_url,
        target_url=target_url,
    )
    shutil.rmtree(mirrors_dir)


def get_full_repo_name_from_url(url: str) -> str:
    ssh_match = re.match(r"git@([^:]+):(.+)", url)
    if ssh_match:
        return ssh_match.group(2)
    https_match = re.match(r"https?://[^/]+/(.+)", url)
    if https_match:
        return https_match.group(1)
    git_match = re.match(r"git://[^/]+/(.+)", url)
    if git_match:
        return git_match.group(1)
    raise ValueError(f"Unable to parse repository URL: {url}")


def load_config(path: str) -> Config:
    with open(path) as f:
        yaml = f.read()
    return from_yaml(Config, yaml)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from dotenv import load_dotenv
from serde.yaml import from_yaml

from .config import Config
from .mover import Mover
from .utils import getenv, getenv_bool

CONFIG_FILE_NAME = "config.yaml"
ARTIFACTS_FOLDER_NAME = "artifacts"


async def main():
    load_dotenv()
    data_dir = getenv("DATA_DIR")
    config_file_path = f"{data_dir}/{CONFIG_FILE_NAME}"
    config = load_config(config_file_path)
    artifacts_folder_path = f"{data_dir}/{ARTIFACTS_FOLDER_NAME}"
    dry_run = getenv_bool("DRY_RUN")

    mover = Mover(
        config=config,
        artifacts_path=artifacts_folder_path,
        dry_run=dry_run,
    )
    await mover.move_all()


def load_config(path: str) -> Config:
    with open(path) as f:
        yaml = f.read()
    return from_yaml(Config, yaml)


if __name__ == "__main__":
    asyncio.run(main())

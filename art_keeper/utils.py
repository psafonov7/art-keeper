import os

import requests

CHUNK_SIZE = 4096


def getenv(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable {key} doesn't exists")
    return value


def getenv_bool(key: str) -> bool:
    str_value = os.getenv(key)
    if str_value is None:
        raise ValueError(f"Environment variable {key} doesn't exists")
    match str_value:
        case "true":
            return True
        case "false":
            return False
        case _:
            raise ValueError(f"Environment variable {key} is not a bool")


def download_file(url: str, path: str):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(path, "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)

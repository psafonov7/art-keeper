import os
import re
from pathlib import Path

import aiofiles
import aiohttp
from aiohttp.client_reqrep import ClientResponse

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


def create_dir(path: str):
    directory_path = Path(path)
    directory_path.mkdir(parents=True, exist_ok=True)


async def download_file(url: str, path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            await _write_file(response, path)


async def _write_file(response: ClientResponse, path: str):
    async with aiofiles.open(path, mode="wb") as f:
        async for chunk in response.content.iter_chunked(CHUNK_SIZE):
            await f.write(chunk)


def get_version(string: str) -> str | None:
    regex = r"(\d+)\.(\d+)\.(\d+)"
    match = re.search(regex, string)
    if match is None:
        return None
    return match.group(1)


def get_substring_between_strings(
    text: str, start_delimiter: str, end_delimiter: str
) -> str | None:
    start_index = text.find(start_delimiter)
    if start_index == -1:
        return None
    start_of_substring = start_index + len(start_delimiter)
    end_index = text.find(end_delimiter, start_of_substring)
    if end_index == -1:
        return None
    return text[start_of_substring:end_index]


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

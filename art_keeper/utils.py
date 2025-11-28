import os

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


async def download_file(url: str, path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            await _write_file(response, path)


async def _write_file(response: ClientResponse, path: str):
    async with aiofiles.open(path, mode="wb") as f:
        async for chunk in response.content.iter_chunked(CHUNK_SIZE):
            await f.write(chunk)

import base64
import binascii
import hashlib
import tempfile

import aiofiles

from .utils import download_file

CHECKSUMS_FILE_NAME = "CHECKSUMS"
CHUNK_SIZE = 4096
DEFAULT_READ_SIZE = 64 * 1024  # 64KB


async def checksums_from_url(url: str) -> dict[str, str]:
    with tempfile.TemporaryDirectory() as tmpdirname:
        file_path = tmpdirname + "/" + CHECKSUMS_FILE_NAME
        try:
            await download_file(url, file_path)
        except ValueError as e:
            print(e)
        return await checksums_from_file(file_path)


async def checksums_from_file(path: str) -> dict[str, str]:
    async with aiofiles.open(path, "r") as f:
        checksums_data = {}
        async for line in f:
            cleaned = " ".join(line.split())
            parts = cleaned.strip().split(" ", 1)
            if len(parts) == 2:
                checksum, filename = parts
                checksums_data[filename] = checksum
        return checksums_data


async def get_file_sha256(file_path: str) -> str | None:
    try:
        async with aiofiles.open(file_path, "rb") as f:
            sha256_hash = hashlib.sha256()
            while True:
                byte_block = await f.read(DEFAULT_READ_SIZE)
                if not byte_block:
                    break
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None


async def get_file_sha256_raw_base64(file_path: str) -> str | None:
    checksum = await get_file_sha256(file_path)
    if checksum is None:
        return None
    return hex_to_base64(checksum)


def base64_to_hex(base64_string: str) -> str:
    raw_bytes = base64.b64decode(base64_string)
    return binascii.hexlify(raw_bytes).decode()


def hex_to_base64(hex_string: str) -> str:
    hex_string = hex_string.strip().lower()
    raw_bytes = binascii.unhexlify(hex_string)
    return base64.b64encode(raw_bytes).decode()

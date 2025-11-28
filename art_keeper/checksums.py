import hashlib
import tempfile

from .utils import download_file

CHECKSUMS_FILE_NAME = "CHECKSUMS"
CHUNK_SIZE = 4096


async def checksums_from_url(url: str) -> dict[str, str]:
    with tempfile.TemporaryDirectory() as tmpdirname:
        file_path = tmpdirname + "/" + CHECKSUMS_FILE_NAME
        try:
            await download_file(url, file_path)
        except ValueError as e:
            print(e)
        return checksums_from_file(file_path)


def checksums_from_file(path: str) -> dict[str, str]:
    checksums_data = {}
    with open(path, "r") as f:
        for line in f:
            cleaned = " ".join(line.split())
            parts = cleaned.strip().split(" ", 1)
            if len(parts) == 2:
                checksum, filename = parts
                checksums_data[filename] = checksum
    return checksums_data


def get_sha256_checksum(file_path: str) -> str | None:
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None

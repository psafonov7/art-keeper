from contextlib import asynccontextmanager

import aiofiles
from aiobotocore.session import get_session
from botocore.exceptions import ClientError

from .checksums import get_file_sha256_raw_base64, hex_to_base64


class S3Client:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region: str = "us-east-1",
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client(
            service_name="s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as client:
            yield client

    async def upload_file(self, object_name: str, file_path: str):
        checksum = await get_file_sha256_raw_base64(file_path)
        if checksum is None:
            raise ValueError(f"Can't calculate checksum for file {file_path}")
        try:
            async with aiofiles.open(file_path, "rb") as f:
                file_data = await f.read()
            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=file_data,
                    ChecksumSHA256=checksum,
                )
                print(f"File {object_name} uploaded to {self.bucket_name}")
        except ClientError as e:
            print(f"Error uploading file: {e}")

    async def is_object_exists(self, object_name: str, expected_checksum: str) -> bool:
        expected_checksum = hex_to_base64(expected_checksum)
        async with self.get_client() as client:
            try:
                info = await client.get_object_attributes(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    ObjectAttributes=["Checksum"],
                )
                s3_checksum = info.get("Checksum").get("ChecksumSHA256")
                match = expected_checksum == s3_checksum
                return match
            except ClientError:
                return False

    async def create_bucket_if_needed(self, name: str):
        exists = await self.is_bucket_exists(name)
        if not exists:
            async with self.get_client() as client:
                await client.create_bucket(Bucket=name)
                print(f"Created bucket {name}")
        else:
            print(f"Bucket {name} already exists")

    async def is_bucket_exists(self, name: str) -> bool:
        try:
            async with self.get_client() as client:
                await client.get_bucket_acl(Bucket=name)
                return True
        except ClientError:
            return False

from minio import Minio
from minio.error import S3Error


class S3Client:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        region: str = "us-east-1",
    ):
        self._client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            region=region,
        )

    def upload_file(self, bucket_name: str, object_name: str, file_path: str):
        self._client.fput_object(bucket_name, object_name, file_path)

    def is_object_exists(
        self, bucket_name: str, object_name: str, checksum: str
    ) -> bool:
        try:
            stats = self._client.stat_object(bucket_name, object_name)
            return stats.etag == checksum
        except S3Error:
            return False

    def create_bucket_if_needed(self, name: str):
        found = self._client.bucket_exists(bucket_name=name)
        if not found:
            self._client.make_bucket(bucket_name=name)
            print(f"Created bucket {name}")
        else:
            print(f"Bucket {name} already exists")

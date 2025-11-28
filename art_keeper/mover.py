import asyncio
import os

from .checksums import CHECKSUMS_FILE_NAME, checksums_from_url
from .config import Config, ConfigFilter
from .filters.filter_sequence import FilterSequence
from .github import Asset, GithubClient, Release
from .s3client import S3Client
from .utils import download_file, getenv


class Mover:
    BUCKET_NAME = "artifacts"
    REPO_NAME = "yannh/kubeconform"
    CHECKSUMS_FILE_NAME = "CHECKSUMS"
    ARTIFACTS_FOLDER_NAME = "artifacts"

    def __init__(
        self,
        config: Config,
        artifacts_path: str,
        dry_run: bool,
    ):
        self.config = config
        self.artifacts_path = artifacts_path
        self.dry_run = dry_run

    async def move_all(self):
        github_client = GithubClient(getenv("GITHUB_TOKEN"))
        releases: list[Release] = []
        try:
            releases = await github_client.get_releases(self.REPO_NAME)
        except ValueError as e:
            print(e)
            return

        s3client = S3Client(
            endpoint=getenv("S3_ENDPOINT"),
            access_key=getenv("S3_ACCESS_KEY_ID"),
            secret_key=getenv("S3_SECRET_ACCESS_KEY"),
            bucket_name=self.BUCKET_NAME,
        )
        await s3client.create_bucket_if_needed(self.BUCKET_NAME)

        tasks = [
            self.move_release(
                release=release,
                config=self.config,
                artifacts_path=self.artifacts_path,
                dry_run=self.dry_run,
                s3client=s3client,
            )
            for release in releases
        ]
        await asyncio.gather(*tasks)

    async def move_release(
        self,
        release: Release,
        config: Config,
        artifacts_path: str,
        dry_run: bool,
        s3client: S3Client,
    ):
        checksums_url, i, ok = self._get_checksum_url(release, CHECKSUMS_FILE_NAME)
        if not ok:
            print(f"Checksums file not found in release {release.tag_name}")
            return
        release.assets.pop(i)
        checksums = await checksums_from_url(checksums_url)
        assets = self.filter_assets(release, config.filters)
        tasks = [
            self.move_asset(
                asset=asset,
                release=release,
                repo_name=self.REPO_NAME,
                checksums=checksums,
                artifacts_path=artifacts_path,
                dry_run=dry_run,
                s3client=s3client,
            )
            for asset in assets
        ]
        await asyncio.gather(*tasks)

    async def move_asset(
        self,
        asset: Asset,
        release: Release,
        repo_name: str,
        checksums: dict[str, str],
        artifacts_path: str,
        dry_run: bool,
        s3client: S3Client,
    ):
        object_name = self.asset_name_correction(asset, release, repo_name)
        print(f"Moving {object_name}")
        if dry_run:
            return
        checksum = checksums[asset.name]
        exists = await s3client.is_object_exists(
            self.BUCKET_NAME, object_name, checksum
        )
        if not exists:
            await self.move_artifact(asset, object_name, artifacts_path, s3client)
        else:
            print(f"Artifact '{object_name}' is alredy exists, skipping")

    def filter_assets(
        self, release: Release, filters: list[ConfigFilter]
    ) -> list[Asset]:
        assets = []
        for asset in release.assets:
            filter_sequence = FilterSequence(filters)
            if not filter_sequence.is_pass(asset.name):
                continue
            assets.append(asset)
        return assets

    async def move_artifact(
        self, asset: Asset, name: str, arts_folder_path: str, s3client: S3Client
    ):
        art_path = arts_folder_path + "/" + name
        try:
            print(f"Downloading {asset.name}")
            await download_file(asset.browser_download_url, art_path)
        except ValueError as e:
            print(f"Download artifact '{asset.name}' error: {e}")
            return
        print(f"Uploading file {name}")
        await s3client.upload_file(self.BUCKET_NAME, name, art_path)
        os.remove(art_path)

    def asset_name_correction(
        self,
        asset: Asset,
        release: Release,
        repo_name: str,
    ) -> str:
        if release.tag_name in asset.name:
            return asset.name
        project_name = repo_name.split("/")[1]
        i = asset.name.find(project_name) + len(project_name) + 1
        if i <= 0:
            raise ValueError("Bad asset naming")
        return asset.name[:i] + release.tag_name + "-" + asset.name[i:]

    def _get_checksum_url(
        self, release: Release, file_name: str
    ) -> tuple[str, int, bool]:
        for i, asset in enumerate(release.assets):
            if file_name == asset.name:
                return (asset.browser_download_url, i, True)
        return ("", -1, False)

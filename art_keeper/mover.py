import asyncio
import os
from typing import Optional

from .checksums import CHECKSUMS_FILE_NAME, checksums_from_url
from .config import Config, ConfigFilter, ConfigRepo
from .filters.filter_sequence import FilterSequence
from .github import Asset, GithubClient, Release
from .s3client import S3Client
from .utils import download_file, get_version, getenv


class Mover:
    BUCKET_NAME = "artifacts"
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
        github_token = getenv("GITHUB_TOKEN")
        github_client = GithubClient(github_token)
        for repo in self.config.repos:
            await self.move_repo(repo, github_client)

    async def move_repo(self, repo: ConfigRepo, github_client: GithubClient):
        s3client = S3Client(
            endpoint=getenv("S3_ENDPOINT"),
            access_key=getenv("S3_ACCESS_KEY_ID"),
            secret_key=getenv("S3_SECRET_ACCESS_KEY"),
            bucket_name=self.BUCKET_NAME,
        )
        await s3client.create_bucket_if_needed(self.BUCKET_NAME)

        page = 1
        releases: list[Release] = []
        while True:
            next_page = await self._get_next_releases(github_client, repo, page)
            if len(next_page) == 0:
                break
            releases.extend(next_page)
            page += 1
        tasks = [
            self.move_release(
                release=release,
                repo_name=repo.name,
                filters=repo.filters,
                artifacts_path=self.artifacts_path,
                dry_run=self.dry_run,
                verify_checksums=repo.verify_checksums,
                s3client=s3client,
            )
            for release in releases
        ]
        await asyncio.gather(*tasks)

    async def _get_next_releases(
        self, github_client: GithubClient, repo: ConfigRepo, page: int
    ) -> list[Release]:
        if repo.last_releases_count:
            if page != 1:
                return []
            try:
                return await github_client.get_releases(
                    repo.name, repo.last_releases_count
                )
            except ValueError as e:
                print(e)
                return []

        try:
            releases = await github_client.get_releases(repo.name, page=page)
        except ValueError as e:
            print(e)
            return []
        return releases

    async def move_release(
        self,
        repo_name: str,
        release: Release,
        filters: Optional[list[ConfigFilter]],
        artifacts_path: str,
        dry_run: bool,
        verify_checksums: bool,
        s3client: S3Client,
    ):
        checksums = {}
        if verify_checksums:
            checksums = await self.checksums_from_release(release)
        assets = release.assets
        if filters:
            assets = self.filter_assets(release.assets, filters)
        tasks = []
        for asset in assets:
            checksum: str | None = None
            if verify_checksums:
                checksum = checksums[asset.name]
            tasks.append(
                self.move_asset(
                    asset=asset,
                    release=release,
                    repo_name=repo_name,
                    checksum=checksum,
                    artifacts_path=artifacts_path,
                    dry_run=dry_run,
                    s3client=s3client,
                )
            )
        await asyncio.gather(*tasks)

    async def checksums_from_release(self, release: Release) -> dict[str, str]:
        checksums_url, i, ok = self._get_checksum_url(release, CHECKSUMS_FILE_NAME)
        if not ok:
            raise ValueError(f"Checksums file not found in release {release.tag_name}")
        release.assets.pop(i)
        return await checksums_from_url(checksums_url)

    async def move_asset(
        self,
        asset: Asset,
        release: Release,
        repo_name: str,
        checksum: str | None,
        artifacts_path: str,
        dry_run: bool,
        s3client: S3Client,
    ):
        object_name = self.asset_name_correction(asset, release, repo_name)
        print(f"Moving {object_name}")
        if dry_run:
            return

        exists = False
        if checksum:
            exists = await s3client.is_object_exists_checksum(object_name, checksum)
        else:
            exists = await s3client.is_object_exists_name(object_name)

        if not exists:
            await self.move_artifact(asset, object_name, artifacts_path, s3client)
        else:
            print(f"Artifact '{object_name}' is alredy exists, skipping")

    def filter_assets(
        self, assets: list[Asset], filters: list[ConfigFilter]
    ) -> list[Asset]:
        filtered = []
        for asset in assets:
            filter_sequence = FilterSequence(filters)
            if not filter_sequence.is_pass(asset.name):
                continue
            filtered.append(asset)
        return filtered

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
        await s3client.upload_file(name, art_path)
        os.remove(art_path)

    def asset_name_correction(
        self,
        asset: Asset,
        release: Release,
        repo_name: str,
    ) -> str:
        tag = release.tag_name
        version = get_version(tag)
        if version is None:
            raise ValueError(f"Version not found in tag: {tag}")
        asset_name = asset.name
        asset_name = asset_name.replace("_", "-")
        if version in asset_name:
            return asset_name
        project_name = repo_name.split("/")[1]
        i = asset_name.find(project_name) + len(project_name) + 1
        if i <= 0:
            raise ValueError("Bad asset naming")
        return asset_name[:i] + release.tag_name + "-" + asset_name[i:]

    def _get_checksum_url(
        self, release: Release, file_name: str
    ) -> tuple[str, int, bool]:
        for i, asset in enumerate(release.assets):
            if file_name == asset.name:
                return (asset.browser_download_url, i, True)
        return ("", -1, False)

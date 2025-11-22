import os

from dotenv import load_dotenv
from serde.yaml import from_yaml

from .checksums import checksums_from_url
from .config import Config
from .filters.filter_sequence import FilterSequence
from .github import Asset, GithubClient, Release
from .s3 import S3Client
from .utils import download_file, getenv, getenv_bool

BUCKET_NAME = "artifacts"
REPO_NAME = "yannh/kubeconform"

CHECKSUMS_FILE_NAME = "CHECKSUMS"

CONFIG_FILE_NAME = "config.yaml"
ARTIFACTS_FOLDER_NAME = "artifacts"


def main():
    load_dotenv()
    data_dir = getenv("DATA_DIR")
    config_file_path = f"{data_dir}/{CONFIG_FILE_NAME}"
    config = load_config(config_file_path)
    artifacts_folder_path = f"{data_dir}/{ARTIFACTS_FOLDER_NAME}"
    dry_run = getenv_bool("DRY_RUN")

    github_client = GithubClient(getenv("GITHUB_TOKEN"))
    releases: list[Release] = []
    try:
        releases = github_client.get_releases(REPO_NAME)
    except ValueError as e:
        print(e)
        return

    s3 = S3Client(
        endpoint=getenv("S3_ENDPOINT"),
        access_key=getenv("S3_ACCESS_KEY_ID"),
        secret_key=getenv("S3_SECRET_ACCESS_KEY"),
    )
    s3.create_bucket_if_needed(BUCKET_NAME)

    for release in releases:
        print(f"---------- Moving {REPO_NAME} {release.tag_name} ----------")
        checksums_url, i, ok = get_checksum_url(release)
        if not ok:
            print(f"Checksums file not found in release {release.tag_name}")
            continue
        release.assets.pop(i)
        checksums = checksums_from_url(checksums_url)
        move_assets(
            config=config,
            release=release,
            repo_name=REPO_NAME,
            checksums=checksums,
            arts_folder_path=artifacts_folder_path,
            dry_run=dry_run,
            s3=s3,
        )


def load_config(path: str) -> Config:
    with open(path) as f:
        yaml = f.read()
    return from_yaml(Config, yaml)


def get_checksum_url(release: Release) -> tuple[str, int, bool]:
    for i, asset in enumerate(release.assets):
        if CHECKSUMS_FILE_NAME == asset.name:
            return (asset.browser_download_url, i, True)
    return ("", -1, False)


def move_assets(
    config: Config,
    release: Release,
    repo_name: str,
    checksums: dict[str, str],
    arts_folder_path: str,
    dry_run: bool,
    s3: S3Client,
):
    for asset in release.assets:
        filter_sequence = FilterSequence(config.filters)
        if not filter_sequence.is_pass(asset.name):
            continue
        object_name = asset_name_correction(asset, release, repo_name)
        print(f"Moving asset {object_name}")
        if dry_run:
            continue
        checksum = checksums[asset.name]
        exists = s3.is_object_exists(BUCKET_NAME, object_name, checksum)
        if not exists:
            move_artifact(asset, object_name, arts_folder_path, s3)
        else:
            print(f"Artifact '{object_name}' is alredy exists, skipping")


def move_artifact(asset: Asset, name: str, arts_folder_path: str, s3: S3Client):
    art_path = arts_folder_path + "/" + name
    try:
        download_file(asset.browser_download_url, art_path)
    except ValueError as e:
        print(f"Download artifact '{asset.name}' error: {e}")
        return
    s3.upload_file(BUCKET_NAME, name, art_path)
    os.remove(art_path)


def asset_name_correction(
    asset: Asset,
    release: Release,
    repo_name: str,
) -> str:
    if release.tag_name in asset.name:
        return asset.name
    print(repo_name)
    project_name = repo_name.split("/")[1]
    i = asset.name.find(project_name) + len(project_name) + 1
    if i <= 0:
        raise ValueError("Bad asset naming")
    return asset.name[:i] + release.tag_name + "-" + asset.name[i:]


if __name__ == "__main__":
    main()

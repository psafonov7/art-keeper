package art_move

import (
	"errors"
	"fmt"
	"log"
	"os"
	"slices"
	"strings"

	"art-keeper/checksums"
	"art-keeper/config"
	"art-keeper/github"
	"art-keeper/s3"
	"art-keeper/utils"
)

const Checksums = "CHECKSUMS"

var ChecksumFileNames = []string{Checksums, "checksums"}

func Setup() {
	s3.Setup()
}

func MoveRepoArtifacts(
	config config.Config,
	repoName string,
	artsFolderPath string,
	dryRun bool,
) {
	client := github.NewClientDefault()
	releases, err := client.GetReleases(repoName)
	if err != nil {
		log.Printf("Get assets from GitHub error: %s", err.Error())
		return
	}
	s3.CreateBucketIfNotExists()
	for _, release := range releases {
		log.Printf("========== Moving %s %s ==========", repoName, release.TagName)
		checksums, assetIdx, err := getChecksums(release, artsFolderPath)
		if err != nil {
			log.Printf("Get checksums from release '%s' error: %s", release.TagName, err.Error())
			continue
		}
		release.Assets = slices.Delete(release.Assets, assetIdx, assetIdx+1)
		moveAssets(config, release, repoName, checksums, artsFolderPath, dryRun)
	}
}

func moveAssets(
	config config.Config,
	release github.Release,
	repoName string,
	checksums map[string]string,
	artsFolderPath string,
	dryRun bool,
) {
	for _, asset := range release.Assets {
		filterSequence := NewFilterSequence(config.Filters)
		if !filterSequence.Pass(asset.Name) {
			continue
		}
		log.Printf("Moving artifact '%s'", asset.Name)
		if dryRun {
			continue
		}

		name := assetNameCorrection(asset, release, repoName)
		exists, err := s3.IsObjectExists(name, checksums[asset.Name])
		if err != nil {
			log.Printf("Object exists check error: %s", err.Error())
			continue
		}
		if !exists {
			moveArtifact(asset, name, artsFolderPath)
		} else {
			log.Printf("Artifact '%s' is alredy exists, skipping", name)
		}
	}
}

func getChecksums(release github.Release, artsFolderPath string) (map[string]string, int, error) {
	url, assetIdx, err := getChecksumsAsset(release)
	if err != nil {
		return map[string]string{}, -1, err
	}
	checksumsPath := artsFolderPath + "/" + Checksums
	if err := utils.DownloadFile(url, checksumsPath); err != nil {
		log.Printf("Checksums file download error: %s", err.Error())
		return map[string]string{}, -1, err
	}
	checksums, err := checksums.ParseChecksumsFromFile(checksumsPath)
	if err != nil {
		return map[string]string{}, -1, err
	}
	return checksums, assetIdx, nil
}

func getChecksumsAsset(release github.Release) (string, int, error) {
	for i, asset := range release.Assets {
		for _, filename := range ChecksumFileNames {
			if asset.Name == filename {
				return asset.Url, i, nil
			}
		}
	}
	errText := fmt.Sprintf("Unable to find checksums asset from repo: %s", release.TagName)
	return "", -1, errors.New(errText)
}

func moveArtifact(asset github.Asset, name string, artsFolderPath string) {
	artPath := artsFolderPath + "/" + name
	if err := utils.DownloadFile(asset.Url, artPath); err != nil {
		log.Printf("Download artifact '%s' error: %s", asset.Name, err.Error())
		return
	}
	if err := s3.UploadFile(artPath, name); err != nil {
		log.Printf("Upload artifact '%s' error: %s", name, err.Error())
		return
	}
	if err := os.Remove(artPath); err != nil {
		log.Printf("Error removing directory %s: %v", artPath, err)
	}
}

func assetNameCorrection(asset github.Asset, release github.Release, repoName string) string {
	if !strings.Contains(asset.Name, release.TagName) {
		namePrefix := strings.Split(repoName, "/")[1] + "-"
		return utils.InsertAfter(asset.Name, namePrefix, release.TagName+"-")
	}
	return asset.Name
}

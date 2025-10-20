package art_move

import (
	"log"
	"strings"

	"art-keeper/github"
	"art-keeper/s3"
	"art-keeper/utils"
)

func MoveRepoArtifacts(repoName string, artsFolderPath string) {
	releases, err := github.GetReleases(repoName)
	if err != nil {
		log.Printf("Get assets from GitHub error: %s", err.Error())
		return
	}
	for _, release := range releases {
		for _, asset := range release.Assets {
			name := assetNameCorrection(asset, release, repoName)
			moveArtifact(asset, name, artsFolderPath)
		}
	}
}

func moveArtifact(asset github.Asset, name string, artsFolderPath string) {
	log.Printf("Moving artifact '%s'", asset.Name)
	artPath := artsFolderPath + "/" + name
	if err := utils.DownloadFile(asset.Url, artPath); err != nil {
		log.Printf("Download artifact '%s' error: %s", asset.Name, err.Error())
		return
	}
	if err := s3.UploadFile(artPath, name); err != nil {
		log.Printf("Upload artifact '%s' error: %s", name, err.Error())
		return
	}
}

func assetNameCorrection(asset github.Asset, release github.Release, repoName string) string {
	if !strings.Contains(asset.Name, release.TagName) {
		namePrefix := strings.Split(repoName, "/")[1] + "-"
		return utils.InsertAfter(asset.Name, namePrefix, release.TagName+"-")
	}
	return asset.Name
}

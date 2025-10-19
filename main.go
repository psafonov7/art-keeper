package main

import (
	"fmt"

	"art-keeper/github"
	"art-keeper/s3"
	"art-keeper/utils"

	"github.com/joho/godotenv"
)

const Repo = "instrumenta/kubeval"

func main() {
	godotenv.Load()

	releases, err := github.GetReleases(Repo)
	if err != nil {
		fmt.Printf("Error: %s", err.Error())
		return
	}
	asset := releases[0].Assets[1]
	err = utils.DownloadFile(asset.Url, asset.Name)
	if err != nil {
		fmt.Printf("Error: %s", err.Error())
		return
	}

	err = s3.UploadFile(asset.Name, asset.Name)
	if err != nil {
		fmt.Printf("Error: %s", err.Error())
		return
	}
}

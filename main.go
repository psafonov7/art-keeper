package main

import (
	"log"
	"os"
	"strings"

	"art-keeper/utils"

	"art-keeper/art_move"

	"art-keeper/config"

	"github.com/goccy/go-yaml"
	"github.com/joho/godotenv"
)

const Workdir = "/etc/art-keeper"
const ConfigPath = Workdir + "/config.yaml"
const ArtifactsPath = Workdir + "/artifacts"

func main() {
	setupWorkDir()
	godotenv.Load()
	art_move.Setup()
	config := parseConfig(ConfigPath)
	for _, repo := range config.Repos {
		art_move.MoveRepoArtifacts(config, repo, ArtifactsPath, IsDryRun())
	}
}

func IsDryRun() bool {
	dry, has := os.LookupEnv("DRY_RUN")
	if has {
		return strings.EqualFold(dry, "true")
	} else {
		return false
	}
}

func setupWorkDir() {
	if err := utils.CreateFolder(Workdir); err != nil {
		log.Fatalf("Can't create workdir at path %s, error: %s", Workdir, err.Error())
	}
	if err := utils.CreateFolder(ArtifactsPath); err != nil {
		log.Fatalf("Can't create artifacts folder at path %s, error: %s", ArtifactsPath, err.Error())
	}
}

func parseConfig(path string) config.Config {
	ymlBytes, err := os.ReadFile(path)
	if err != nil {
		log.Fatalf("Unable to read file: %s", err.Error())
	}
	config := config.Config{}
	if err := yaml.Unmarshal([]byte(ymlBytes), &config); err != nil {
		log.Fatalf("Config parsing error: %s", err.Error())
	}
	return config
}

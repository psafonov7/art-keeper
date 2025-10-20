package main

import (
	"log"
	"os"

	"art-keeper/utils"

	"art-keeper/art_move"

	"github.com/goccy/go-yaml"
	"github.com/joho/godotenv"
)

type Config struct {
	Repos []string `yaml:"repos"`
}

const Workdir = "/etc/art-keeper"
const ConfigPath = Workdir + "/config.yaml"
const ArtifactsPath = Workdir + "/artifacts"

func main() {
	setupWorkDir()
	godotenv.Load()
	config := parseConfig(ConfigPath)
	for _, repo := range config.Repos {
		art_move.MoveRepoArtifacts(repo, ArtifactsPath)
	}
}

func setupWorkDir() {
	if err := utils.CreateFolder(Workdir); err != nil {
		log.Fatalf("Can't create workdir at path '%s', error: %s", Workdir, err.Error())
	}
	if err := utils.CreateFolder(ArtifactsPath); err != nil {
		log.Fatalf("Can't create artifacts folder at path '%s', error: %s", Workdir, err.Error())
	}
}

func parseConfig(path string) Config {
	ymlBytes, err := os.ReadFile(path)
	if err != nil {
		log.Fatalf("Unable to read file: %s", err.Error())
	}
	config := Config{}
	if err := yaml.Unmarshal([]byte(ymlBytes), &config); err != nil {
		log.Fatalf("Config parsing error: %s", err.Error())
	}
	return config
}

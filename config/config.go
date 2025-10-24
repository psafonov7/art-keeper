package config

// import "art-keeper/art_move"

type Config struct {
	Repos   []string     `yaml:"repos"`
	Filters []FilterConf `yaml:"filters"`
}

type FilterConf struct {
	Type  string `yaml:"type"`
	Value string `yaml:"value"`
}

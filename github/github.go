package github

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

type Asset struct {
	Url  string `json:"browser_download_url"`
	Name string `json:"name"`
	Size int    `json:"size"`
}

type Release struct {
	Url         string  `json:"url"`
	TagName     string  `json:"tag_name"`
	PublishedAt string  `json:"published_at"`
	Assets      []Asset `json:"assets"`
}

const GithubApiUrl = "https://api.github.com"
const GithubTokenEnv = "GITHUB_TOKEN"

func GetReleases(repo string) ([]Release, error) {
	url := fmt.Sprintf("%s/repos/%s/releases", GithubApiUrl, repo)
	resp, err := get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	var releases []Release
	err = json.NewDecoder(resp.Body).Decode(&releases)
	return releases, err
}

func get(url string) (*http.Response, error) {
	githubToken := os.Getenv(GithubTokenEnv)
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", githubToken))
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	return resp, nil
}

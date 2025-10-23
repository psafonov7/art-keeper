package github

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
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

type Client struct {
	BaseURL string
	Token   string
	Client  *http.Client
}

func NewClientDefault() *Client {
	return NewClient(
		"https://api.github.com",
		os.Getenv("GITHUB_TOKEN"),
		&http.Client{Timeout: 10 * time.Second},
	) 
}

func NewClient(baseUrl string, token string, client *http.Client) *Client {
	return &Client{
		BaseURL: baseUrl,
		Token:   token,
		Client:  client,
	}
}

func (c *Client) GetReleases(repo string) ([]Release, error) {
	url := fmt.Sprintf("%s/repos/%s/releases", c.BaseURL, repo)
	resp, err := get(url, c.Token, c.Client)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	var releases []Release
	err = json.NewDecoder(resp.Body).Decode(&releases)
	return releases, err
}

func get(url string, token string, client *http.Client) (*http.Response, error) {
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", token))
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	return resp, nil
}

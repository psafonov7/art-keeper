package checksums

import (
	"bufio"
	"crypto/sha256"
	"fmt"
	"io"
	"os"
	"strings"
)

func ParseChecksumsFromFile(path string) (map[string]string, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	checksums := make(map[string]string)
	for scanner.Scan() {
		line := scanner.Text()
		split := strings.Split(line, " ")
		checksums[split[0]] = split[1]
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}

	return checksums, nil
}

func GetFileChecksum(path string) (string, error) {
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()

	hash := sha256.New()
	if _, err := io.Copy(hash, file); err != nil {
		return "", err
	}
	hashStr := fmt.Sprintf("%x", hash.Sum(nil))
	return hashStr, nil
}

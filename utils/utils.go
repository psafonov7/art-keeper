package utils

import (
	"io"
	"net/http"
	"os"
	"strconv"
	"strings"
)

func DownloadFile(url string, filepath string) error {
	out, err := os.Create(filepath)
	if err != nil {
		return err
	}
	defer out.Close()

	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	_, err = io.Copy(out, resp.Body)
	if err != nil {
		return err
	}

	return nil
}

func InsertAfter(original string, word string, insert string) string {
	index := strings.Index(original, word)
	if index == -1 {
		return original
	}
	insertPos := index + len(word)
	return original[:insertPos] + insert + original[insertPos:]
}

func CreateFolder(path string) error {
	return createFolderWithMod(path, "0744", false)
}

func CreateFolderRec(path string) error {
	return createFolderWithMod(path, "0744", true)
}

func createFolderWithMod(path string, mod string, recursive bool) error {
	var dirMod uint64
	dirMod, err := strconv.ParseUint(mod, 8, 32)
	if err != nil {
		return err
	}
	if recursive {
		return os.MkdirAll(path, os.FileMode(dirMod))
	} else {
		if _, err := os.Stat(path); os.IsNotExist(err) {
			return os.Mkdir(path, os.FileMode(dirMod))
		}
		return nil
	}
}

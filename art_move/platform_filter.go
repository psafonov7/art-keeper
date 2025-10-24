package art_move

import (
	"fmt"
)

type PlatformFilter struct {
	Platform Platform
}

func NewPlatformFilter(platform string) *PlatformFilter {
	has, p := HasPlatform(platform)
	if has {
		return &PlatformFilter{p}
	} else {
		t := fmt.Sprintf("Error: platform '%s' doesn't exists", platform)
		panic(t)
	}
}

func (f PlatformFilter) Pass(platform string) bool {
	return f.Platform.StrContains(platform)
}

package art_move

import (
	"slices"
	"strings"
)

type Platform int

const (
	PlatformNone Platform = iota
	PlatformLinux
	PlatformWindows
	PlatformMacOS
)

var allPlatforms = []Platform{PlatformLinux, PlatformWindows, PlatformMacOS}

var platformNames = map[Platform][]string{
	PlatformLinux:   {"linux"},
	PlatformWindows: {"windows", "win"},
	PlatformMacOS:   {"darwin", "macos", "mac-os"},
}

func (p Platform) names() []string {
	return platformNames[p]
}

func (p Platform) HasName(n string) bool {
	return slices.Contains(p.names(), n)
}

func (p Platform) StrContains(s string) bool {
	for _, pl := range p.names() {
		if strings.Contains(s, pl) {
			return true
		}
	}
	return false
}

func HasPlatform(s string) (bool, Platform) {
	for _, platform := range allPlatforms {
		if slices.Contains(platform.names(), s) {
			return true, platform
		}
	}
	return false, PlatformNone
}

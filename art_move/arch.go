package art_move

import (
	"slices"
	"strings"
)

type Arch int

const (
	ArchNone Arch = iota
	ArchX8664
	ArchArm64
)

var allArchs = []Arch{ArchX8664, ArchArm64}

var archNames = map[Arch][]string{
	ArchX8664: {"x86_64", "x86-64", "amd64"},
	ArchArm64: {"arm64"},
}

func (a Arch) names() []string {
	return archNames[a]
}

func (a Arch) HasName(n string) bool {
	return slices.Contains(a.names(), n)
}

func (a Arch) StrContains(s string) bool {
	for _, ar := range a.names() {
		if strings.Contains(s, ar) {
			return true
		}
	}
	return false
}

func HasArch(s string) (bool, Arch) {
	for _, arch := range allArchs {
		if slices.Contains(arch.names(), s) {
			return true, arch
		}
	}
	return false, ArchNone
}

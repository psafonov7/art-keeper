package art_move

import (
	"fmt"
)

type ArchFilter struct {
	Arch Arch
}

func NewArchFilter(arch string) ArchFilter {
	has, a := HasArch(arch)
	if has {
		return ArchFilter{a}
	} else {
		t := fmt.Sprintf("Error: arch '%s' doesn't exists", arch)
		panic(t)
	}
}

func (f ArchFilter) Pass(value string) bool {
	return f.Arch.StrContains(value)
}

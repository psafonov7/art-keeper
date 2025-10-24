package art_move

import (
	"art-keeper/config"
	"fmt"
)

type FilterSequence struct {
	Filters []Filter
}

func (s FilterSequence) Pass(value string) bool {
	for _, f := range s.Filters {
		if !f.Pass(value) {
			return false
		}
	}
	return true
}

func NewFilterSequence(confs []config.FilterConf) FilterSequence {
	filters := []Filter{}
	for _, c := range confs {
		f := filterFromConf(c)
		filters = append(filters, f)
	}
	return FilterSequence{filters}
}

func filterFromConf(c config.FilterConf) Filter {
	switch c.Type {
	case "arch":
		return NewArchFilter(c.Value)
	case "platform":
		return NewPlatformFilter(c.Value)
	default:
		t := fmt.Sprintf("Filter with type '%s' doesn't exists", c.Type)
		panic(t)
	}
}

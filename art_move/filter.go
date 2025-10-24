package art_move

type Filter interface {
	Pass(value string) bool
}

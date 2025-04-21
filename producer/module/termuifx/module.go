package termuifx

import (
	"github.com/EelisK/artbit/internal/kernel"
	"github.com/EelisK/artbit/internal/kernel/termui"
	"go.uber.org/fx"
)

type Param struct {
	fx.In
}

type Result struct {
	fx.Out

	UI kernel.TermUI
}

func NewTCell(p Param) (Result, error) {
	ui, err := termui.NewTCell()
	return Result{UI: ui}, err
}

func NewNull(p Param) (Result, error) {
	return Result{UI: termui.NewNull()}, nil
}

// Module provides a tcell based terminal UI.
var TCellModule = fx.Module("termui:tcell", fx.Provide(NewTCell))

// NullModule provides a null terminal UI.
var NullModule = fx.Module("termui:null", fx.Provide(NewNull))

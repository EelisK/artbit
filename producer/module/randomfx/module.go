package randomfx

import (
	"github.com/EelisK/artbit/internal/kernel"
	"github.com/EelisK/artbit/internal/plugin/random"
	"go.uber.org/fx"
)

type Param struct {
	fx.In
}

type Result struct {
	fx.Out

	Source kernel.Source
}

func New(p Param) Result {
	return Result{Source: random.NewSource()}
}

// Module provides a random kernel source.
var Module = fx.Module("random", fx.Provide(New))

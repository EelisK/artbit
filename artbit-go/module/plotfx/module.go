package plotfx

import (
	"github.com/EelisK/artbit/internal/kernel"
	"github.com/EelisK/artbit/internal/plugin/plot"
	"go.uber.org/fx"
)

const (
	DefaultWidth = 100
)

type Param struct {
	fx.In

	Kernel *kernel.Kernel
}

type Result struct {
	fx.Out

	Output *plot.Sink
}

func New(p Param) Result {
	sink := plot.NewStderr(DefaultWidth)
	return Result{Output: sink}
}

// Module provides the plot output sink to the kernel.
// Kernel is assumed to be already present in the context.
var Module = fx.Module("plot",
	fx.Provide(New),
	fx.Invoke(func(k *kernel.Kernel, o *plot.Sink) {
		k.AddSink(o)
	}),
)

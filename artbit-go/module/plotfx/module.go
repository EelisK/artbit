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

// Module provides the plot output sink to the kernel.
// Kernel is assumed to be already present in the context.
var Module = fx.Module("plot",
	fx.Invoke(func(kernel *kernel.Kernel) {
		kernel.AddSink(plot.NewStderr(DefaultWidth))
	}),
)

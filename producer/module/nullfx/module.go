package nullfx

import (
	"github.com/EelisK/artbit/internal/kernel"
	"github.com/EelisK/artbit/internal/plugin/null"
	"go.uber.org/fx"
)

type Param struct {
	fx.In
}

type Result struct {
	fx.Out

	Sink *null.Sink
}

func New(Param) Result {
	return Result{Sink: &null.Sink{}}
}

// Module provides a random kernel source.
var Module = fx.Module(
	"random",
	fx.Provide(New),
	fx.Invoke(func(k *kernel.Kernel, sink *null.Sink) {
		k.AddSink(sink)
	}),
)

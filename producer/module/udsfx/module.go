package udsfx

import (
	"fmt"
	"time"

	"github.com/EelisK/artbit/internal/kernel"
	"github.com/EelisK/artbit/internal/plugin/uds"
	"go.uber.org/fx"
)

type Param struct {
	fx.In

	Kernel *kernel.Kernel
	Config *Config
}

type Result struct {
	fx.Out

	Output *uds.Sink
}

type Config struct {
	SocketPath string        `json:"socket_path"`
	Timeout    time.Duration `json:"timeout"`
}

func New(p Param) (Result, error) {
	if p.Config == nil {
		return Result{}, fmt.Errorf("config is nil")
	}
	sink := uds.NewSink(p.Config.SocketPath, p.Config.Timeout)
	return Result{Output: sink}, nil
}

// Module provides the plot output sink to the kernel.
// Kernel is assumed to be already present in the context.
var Module = fx.Module("plot",
	fx.Provide(New),
	fx.Invoke(func(k *kernel.Kernel, o *uds.Sink) {
		k.AddSink(o)
	}),
)

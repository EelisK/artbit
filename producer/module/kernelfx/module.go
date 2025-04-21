package kernelfx

import (
	"context"

	"github.com/EelisK/artbit/internal/kernel"
	"go.uber.org/fx"
)

type Param struct {
	fx.In

	Source kernel.Source
	UI     kernel.TermUI
}

type Result struct {
	fx.Out

	Kernel *kernel.Kernel
}

func New(p Param) Result {
	// Initialize the kernel with the provided source
	k := kernel.New(p.Source, p.UI)
	return Result{Kernel: k}
}

// Module provides the kernel to the context.
// It is assumed that the source is already present in the context.
var Module = fx.Module(
	"kernel",
	fx.Provide(New),
	fx.Invoke(func(k *kernel.Kernel, lc fx.Lifecycle) {
		lc.Append(fx.Hook{
			OnStart: func(ctx context.Context) error {
				if err := k.Start(ctx); err != nil {
					return err
				}
				return nil
			},
			OnStop: func(ctx context.Context) error {
				return k.Stop(ctx)
			},
		})
	}),
)

package mcp3008fx

import (
	"github.com/EelisK/artbit/internal/kernel"
	"github.com/EelisK/artbit/internal/plugin/mcp3008"
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
	source := mcp3008.NewSource()
	return Result{Source: source}
}

// Module provides the MCP3008 source to the kernel.
// Kernel is initialized later in the context.
var Module = fx.Module("mcp3008", fx.Provide(New))

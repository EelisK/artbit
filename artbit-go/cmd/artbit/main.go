package main

import (
	"log"
	"os"

	"github.com/EelisK/artbit/module/kernelfx"
	"github.com/EelisK/artbit/module/mcp3008fx"
	"github.com/EelisK/artbit/module/plotfx"
	"github.com/EelisK/artbit/module/randomfx"
	"github.com/spf13/cobra"
	"go.uber.org/fx"
)

var includePlot bool

var rootCmd = &cobra.Command{
	Use:   "artbit",
	Short: "Artbit is a tool for creating art raspberry pi projects.",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return cmd.Help()
	},
}

var randomCmd = &cobra.Command{
	Use:   "random",
	Short: "Run the artbit application with random input",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return setupAndRun(
			randomfx.Module,
			kernelfx.Module,
		)
	},
}

var mcp3008Cmd = &cobra.Command{
	Use:   "mcp3008",
	Short: "Run the artbit application with MCP3008 input",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return setupAndRun(
			mcp3008fx.Module,
			kernelfx.Module,
		)
	},
}

func init() {
	rootCmd.PersistentFlags().
		BoolVar(
			&includePlot,
			"plot",
			false,
			"Include plot module",
		)
	rootCmd.AddCommand(randomCmd)
	rootCmd.AddCommand(mcp3008Cmd)
}

func setupAndRun(opts ...fx.Option) error {
	if includePlot {
		opts = append(opts, plotfx.Module)
	}
	app := fx.New(opts...)
	if err := app.Err(); err != nil {
		return err
	}
	app.Run()
	return nil
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		log.Printf("failed to execute command. err: %v", err)
		os.Exit(1)
	}
}

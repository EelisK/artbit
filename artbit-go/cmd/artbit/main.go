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
		return runApp(fx.New(
			randomfx.Module,
			kernelfx.Module,
			// plotfx.Module,
		))
	},
}

var mcp3008Cmd = &cobra.Command{
	Use:   "mcp3008",
	Short: "Run the artbit application with MCP3008 input",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return runApp(fx.New(
			mcp3008fx.Module,
			kernelfx.Module,
			plotfx.Module,
		))
	},
}

func init() {
	rootCmd.AddCommand(randomCmd)
	rootCmd.AddCommand(mcp3008Cmd)
}

func runApp(app *fx.App) error {
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

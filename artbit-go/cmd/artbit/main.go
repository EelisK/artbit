package main

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/EelisK/artbit/module/kernelfx"
	"github.com/EelisK/artbit/module/mcp3008fx"
	"github.com/EelisK/artbit/module/randomfx"
	"github.com/EelisK/artbit/module/termuifx"
	"github.com/EelisK/artbit/module/udsfx"
	"github.com/spf13/cobra"
	"go.uber.org/fx"
)

var (
	developmentMode bool
	inputType       string
	outputTypes     []string
	outputUDSConfig udsfx.Config
)

var rootCmd = &cobra.Command{
	Use:   "artbit",
	Short: "Artbit is a tool for creating art raspberry pi projects.",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return cmd.Help()
	},
}

var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Run the artbit application",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return setupAndRun()
	},
}

func init() {
	rootCmd.PersistentFlags().
		StringVar(&inputType, "input", "random", "Input type (random or mcp3008)")
	rootCmd.PersistentFlags().
		StringArrayVar(&outputTypes, "output", []string{}, "Output types (uds)")
	rootCmd.PersistentFlags().
		StringVar(&outputUDSConfig.SocketPath, "output-uds-socket", "/tmp/artbit.sock", "Socket path for UDS output")
	rootCmd.PersistentFlags().
		DurationVar(&outputUDSConfig.Timeout, "output-uds-timeout", 100*time.Millisecond, "Timeout for UDS output")
	rootCmd.PersistentFlags().
		BoolVar(&developmentMode, "dev", false, "Enable development mode")
	rootCmd.AddCommand(runCmd)
}

func setupAndRun() error {
	opts := []fx.Option{
		kernelfx.Module,
	}

	if developmentMode {
		opts = append(opts, termuifx.TCellModule)
	} else {
		opts = append(opts, termuifx.NullModule)
	}

	switch inputType {
	case "random":
		opts = append(opts, randomfx.Module)
	case "mcp3008":
		opts = append(opts, mcp3008fx.Module)
	default:
		return fmt.Errorf("invalid input type: %s", inputType)
	}

	if len(outputTypes) == 0 {
		return fmt.Errorf("no output types specified")
	}

	for _, outputType := range outputTypes {
		switch outputType {
		case "uds":
			opts = append(opts, fx.Supply(&outputUDSConfig), udsfx.Module)
		default:
			return fmt.Errorf("invalid output type: %s", outputType)
		}
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

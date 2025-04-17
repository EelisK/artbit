package kernel

import (
	"context"
	"time"

	"github.com/EelisK/artbit/internal/kernel/streamstat"
	"golang.org/x/sync/errgroup"
)

// Kernel is a kernel that manages a source and multiple sinks.
type Kernel struct {
	Source   Source
	Sinks    []Sink
	Interval time.Duration
}

const (
	DefaultInterval = 2 * time.Millisecond
)

// New creates a new Default kernel with the given source.
func New(source Source) *Kernel {
	return &Kernel{Source: source, Interval: DefaultInterval}
}

func (k *Kernel) SetInterval(interval time.Duration) {
	k.Interval = interval
}

// AddSink adds a new output sink to the kernel.
func (k *Kernel) AddSink(sink Sink) {
	k.Sinks = append(k.Sinks, sink)
}

// Stop stops the kernel, including the source and all sinks.
func (k *Kernel) Stop(context.Context) error {
	if err := k.Source.Stop(); err != nil {
		return err
	}

	for _, sink := range k.Sinks {
		if err := sink.Stop(); err != nil {
			return err
		}
	}

	return nil
}

// Start starts the kernel, including the source and all sinks.
func (k *Kernel) Start(context.Context) error {
	if err := k.Source.Start(); err != nil {
		return err
	}

	sourceCh := make(chan float64)

	// Start reading from the source
	go func() {
		defer close(sourceCh)
		ticker := time.NewTicker(k.Interval)
		defer ticker.Stop()
		for range ticker.C {
			value, err := k.Source.Read()
			if err != nil {
				continue
			}
			sourceCh <- value
		}
	}()

	// Initialize value processors
	rollingAvg := streamstat.NewAVG(20)
	rollingMinMaxScaler := streamstat.NewMovingMinMaxScaler(2000)
	filters := []func(float64) bool{
		// Sensible values only
		// func(value float64) bool {
		// 	minVal, maxVal := rollingMinMaxScaler.Get()
		// 	size := maxVal - minVal
		// 	return size > 0.1 && size < 0.9
		// },
	}

	for value := range sourceCh {
		// Add value to processors
		rollingAvg.Add(value)
		rollingMinMaxScaler.Add(value)

		// Check if processors are ready
		if !rollingAvg.Ready() {
			continue
		}
		if !rollingMinMaxScaler.Ready() {
			continue
		}

		// Transform value
		value = rollingAvg.Get()
		value = rollingMinMaxScaler.Scale(value)
		for _, filter := range filters {
			if !filter(value) {
				continue
			}
		}

		// Output to sinks
		eg := errgroup.Group{}
		for _, sink := range k.Sinks {
			eg.Go(func() error {
				return sink.Write(value)
			})
		}
		if err := eg.Wait(); err != nil {
			return err
		}
	}

	return nil
}

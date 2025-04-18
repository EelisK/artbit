package kernel

import (
	"context"
	"log"
	"time"

	"github.com/EelisK/artbit/internal/kernel/waveform"
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

var logger = log.New(log.Writer(), "kernel: ", log.LstdFlags)

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

	for _, sink := range k.Sinks {
		if err := sink.Start(); err != nil {
			return err
		}
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

	periodDetector := waveform.NewPeriodDetector(0.8)

	// Set period limits to a sensible range
	periodDetector.SetPeriodLimit(waveform.TimeLimit{
		Min: 333 * time.Millisecond,  // 180 BPM
		Max: 1500 * time.Millisecond, // 40 BPM
	})

	// Set wave value limits to a sensible range
	periodDetector.SetValueLimit(waveform.NumericLimit{
		Min: 0.1,
		Max: 0.98,
	})
	// Set wave amplitude limits to a sensible range
	periodDetector.SetAmplitudeLimit(waveform.NumericLimit{
		Min: 0.1,
		Max: 0.9,
	})

	periodDetector.OnPeriod(func(period time.Duration) {
		value := 60 / period.Seconds()
		// Output to sinks
		eg := errgroup.Group{}
		for _, sink := range k.Sinks {
			eg.Go(func() error {
				return sink.Write(value)
			})
		}
		if err := eg.Wait(); err != nil {
			logger.Printf("failed to write to sink: %v", err)
		}
	})

	for value := range sourceCh {
		// Update period detector
		value = periodDetector.Update(value)
	}

	return nil
}

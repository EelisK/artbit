package random

import (
	"math"
	"time"
)

type Source struct {
	counter   uint64
	startTime time.Time
	noise     *NoiseGenerator
}

func NewSource() *Source {
	return &Source{
		counter: 0,
		noise:   &NoiseGenerator{},
	}
}

func (s *Source) Start() error {
	s.startTime = time.Now()
	return s.noise.Start()
}

func (s *Source) Read() (float64, error) {
	noise, err := s.noise.Read()
	if err != nil {
		return 0, err
	}

	value := s.newWaveValue()
	value += noise
	value = math.Min(math.Max(value, 0), 1)
	return value, nil
}

func (s *Source) Stop() error {
	return s.noise.Stop()
}

func (s *Source) newWaveValue() float64 {
	currentTime := time.Now()
	samplePeriod := currentTime.Sub(s.startTime).Seconds()
	wavePeriod := 1.3
	value := math.Sin(2*math.Pi*wavePeriod*samplePeriod) / 2
	return scale(value, 0.3, 0.7)
}

// scale scales a value from one range to another
func scale(value, min, max float64) float64 {
	return value*(max-min) + min
}

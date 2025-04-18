package random

import (
	"math"
	"math/rand/v2"
)

type Source struct {
	randomCounter int
	randomIndex   int
	counter       uint64
}

func NewSource() *Source {
	return &Source{
		randomCounter: 0,
		randomIndex:   rand.Int() % 100,
	}
}

func (s *Source) Start() error {
	return nil
}

func (s *Source) Read() (float64, error) {
	value := s.newWaveValue()
	value += s.getRandomness()
	value = math.Min(math.Max(value, 0), 1)
	return value, nil
}

func (s *Source) Stop() error {
	return nil
}

func (s *Source) getRandomness() float64 {
	s.randomCounter++
	if s.randomCounter >= s.randomIndex {
		s.randomIndex = rand.Int() % 100
		s.randomCounter = 0
		return newRandom(-1, 1)
	}
	return 0
}

// creates a random number between start and end
func newRandom(start, end float64) float64 {
	return start + rand.Float64()*(end-start)
}

func (s *Source) newWaveValue() float64 {
	// value is a sine wave with a period of 1.3 seconds and amplitude of 0.3
	samplePeriod := 0.002
	sampleFrequency := 1 / samplePeriod
	frequency := 1.3
	value := math.Sin(2*math.Pi*frequency*float64(s.counter)/sampleFrequency) / 2
	value += 0.5
	// now value is between 0 and 1
	// so we add scale it to an amplitude range of 0.3 - 0.7
	rangeStart := 0.3
	rangeEnd := 0.7
	value = value*(rangeEnd-rangeStart) + rangeStart
	s.counter++
	return value
}

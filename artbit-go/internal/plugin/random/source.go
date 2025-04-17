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
	// value is a sine wave with a period of 1.3 seconds
	samplePeriod := 0.002
	sampleFrequency := 1 / samplePeriod
	frequency := 1.3
	value := math.Sin(2*math.Pi*frequency*float64(s.counter)/sampleFrequency) / 2
	value += 0.5
	s.counter++
	s.randomCounter++
	if s.randomCounter >= s.randomIndex {
		s.randomIndex = rand.Int() % 100
		s.randomCounter = 0
		value += newRandom()
		value = math.Min(math.Max(value, 0), 1)
	}
	return value, nil
}

func (s *Source) Stop() error {
	return nil
}

// creates a random number between -1 and 1
func newRandom() float64 {
	return rand.Float64()*2 - 1
}

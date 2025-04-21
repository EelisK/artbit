package random

import "math/rand/v2"

type NoiseGenerator struct {
	counter int
	index   int
}

func (n *NoiseGenerator) Start() error {
	n.counter = 0
	n.index = rand.Int() % 100
	return nil
}

func (n *NoiseGenerator) Read() (float64, error) {
	n.counter++
	if n.counter >= n.index {
		n.index = rand.Int() % 100
		n.counter = 0
		return scale(rand.Float64(), -0.1, 0.1), nil
	}
	return 0, nil
}

func (n *NoiseGenerator) Stop() error {
	return nil
}

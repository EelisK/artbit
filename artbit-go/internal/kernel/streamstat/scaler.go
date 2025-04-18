package streamstat

// TODO: optimize
type MinMaxScaler struct {
	windowSize int
	values     []float64
}

func NewMinMaxScaler(windowSize int) *MinMaxScaler {
	return &MinMaxScaler{
		windowSize: windowSize,
	}
}

func (m *MinMaxScaler) Add(value float64) {
	// Redact the oldest value if the window is full
	if len(m.values) >= m.windowSize {
		m.values = m.values[1:]
	}

	m.values = append(m.values, value)
}

func (m *MinMaxScaler) Get() (float64, float64) {
	if len(m.values) == 0 {
		return 0, 0
	}
	min := m.values[0]
	max := m.values[0]
	for _, v := range m.values {
		if v < min {
			min = v
		}
		if v > max {
			max = v
		}
	}
	return min, max
}

func (s *MinMaxScaler) GetRange() float64 {
	min, max := s.Get()
	return max - min
}

func (m *MinMaxScaler) Scale(value float64) float64 {
	min, max := m.Get()
	if min == max {
		return value
	}
	// scale to [0, 1]
	value = (value - min) / (max - min)
	return value
}

func (m *MinMaxScaler) Ready() bool {
	return len(m.values) >= m.windowSize
}

func (m *MinMaxScaler) Reset() {
	m.values = make([]float64, 0)
}

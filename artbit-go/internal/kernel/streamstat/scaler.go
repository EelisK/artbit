package streamstat

// TODO: optimize
type MinMaxScaler struct {
	windowSize int
	minVals    []float64
	maxVals    []float64
}

func NewMovingMinMaxScaler(windowSize int) *MinMaxScaler {
	return &MinMaxScaler{
		windowSize: windowSize,
		minVals:    make([]float64, 0, windowSize),
		maxVals:    make([]float64, 0, windowSize),
	}
}

func (m *MinMaxScaler) Add(value float64) {
	// Redact the oldest value if the window is full
	if len(m.minVals) >= m.windowSize {
		m.minVals = m.minVals[1:]
		m.maxVals = m.maxVals[1:]
	}

	m.minVals = append(m.minVals, value)
	m.maxVals = append(m.maxVals, value)
}

func (m *MinMaxScaler) Get() (float64, float64) {
	if len(m.minVals) == 0 {
		return 0, 0
	}
	min := m.minVals[0]
	max := m.maxVals[0]
	for _, v := range m.minVals {
		if v < min {
			min = v
		}
	}
	for _, v := range m.maxVals {
		if v > max {
			max = v
		}
	}
	return min, max
}

func (m *MinMaxScaler) Scale(value float64) float64 {
	min, max := m.Get()
	if min == max {
		return value
	}
	return (value - min) / (max - min)
}

func (m *MinMaxScaler) Ready() bool {
	return len(m.minVals) >= m.windowSize
}

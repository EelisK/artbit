package streamstat

type AVG struct {
	windowSize int
	values     []float64
	sum        float64
	index      int
	count      int
}

func NewAVG(windowSize int) *AVG {
	return &AVG{
		windowSize: windowSize,
		values:     make([]float64, windowSize),
	}
}

func (m *AVG) Add(value float64) {
	// Redact the oldest value if the window is full
	if m.Ready() {
		m.sum -= m.values[m.index]
	}

	m.values[m.index] = value
	m.sum += value
	m.count = min(m.count+1, m.windowSize)
	m.index = (m.index + 1) % m.windowSize
}

func (m *AVG) Get() float64 {
	if m.count == 0 {
		return 0
	}
	return m.sum / float64(m.count)
}

func (m *AVG) Ready() bool {
	return m.count >= m.windowSize
}

func (m *AVG) Reset() {
	m.values = make([]float64, m.windowSize)
	m.sum = 0
	m.index = 0
	m.count = 0
}

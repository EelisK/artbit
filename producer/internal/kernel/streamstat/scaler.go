package streamstat

// MinMax maintains a sliding window of values and provides
// scaled values between 0 and 1 based on the min and max in the window.
type MinMax struct {
	windowSize int
	min        *Min
	max        *Max
}

// NewMinMax initializes a new WindowedMinMaxScaler.
func NewMinMax(windowSize int) *MinMax {
	return &MinMax{
		windowSize: windowSize,
		min:        NewMin(windowSize),
		max:        NewMax(windowSize),
	}
}

// Add adds a new value to the scaler and removes the oldest value if the window is full.
func (s *MinMax) Add(value float64) {
	s.min.Add(value)
	s.max.Add(value)
}

// Scale scales the given value to the range [0, 1] based on the current window.
func (s *MinMax) Scale(value float64) float64 {
	min := s.min.Value()
	max := s.max.Value()
	if min == max {
		return 0.5 // Avoid division by zero
	}
	return (value - min) / (max - min)
}

func (s *MinMax) GetRange() float64 {
	return s.max.Value() - s.min.Value()
}

// IsReady checks if the scaler is ready to provide scaled values.
func (s *MinMax) Ready() bool {
	return s.min.Ready() && s.max.Ready()
}

// Reset clears the scaler's state.
func (s *MinMax) Reset() {
	s.min.Reset()
	s.max.Reset()
}

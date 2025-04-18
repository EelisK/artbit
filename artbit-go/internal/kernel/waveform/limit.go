package waveform

import (
	"fmt"
	"time"
)

type TimeLimit struct {
	Min time.Duration
	Max time.Duration
}

func (t TimeLimit) IsInRange(value time.Duration) bool {
	if t.Min > 0 && value < t.Min {
		return false
	}
	if t.Max > 0 && value > t.Max {
		return false
	}
	return true
}

func (t TimeLimit) String() string {
	return fmt.Sprintf("[%s, %s]", t.Min.String(), t.Max.String())
}

type NumericLimit struct {
	Min float64
	Max float64
}

func (n NumericLimit) IsInRange(value float64) bool {
	if n.Min > 0 && value < n.Min {
		return false
	}
	if n.Max > 0 && value > n.Max {
		return false
	}
	return true
}

func (n NumericLimit) String() string {
	return fmt.Sprintf("[%.2f, %.2f]", n.Min, n.Max)
}

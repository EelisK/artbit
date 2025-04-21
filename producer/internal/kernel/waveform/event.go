package waveform

import "time"

// PeriodListener is a function type for period event listeners.
type PeriodListener func(period time.Duration)

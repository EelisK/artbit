package waveform

import (
	"time"

	"github.com/EelisK/artbit/internal/kernel/streamstat"
)

// PeriodDetector is a simple period detector.
type PeriodDetector struct {
	threshold float64

	listeners []EventListener

	prevHighStart time.Time
	prevHighEnd   time.Time
	prevHigh      time.Time

	periodCount uint64

	limit PeriodLimit

	rollingAvg *streamstat.AVG
}

type PeriodLimit struct {
	Min time.Duration
	Max time.Duration
}

// NewPeriodDetector creates a new PeriodDetector with the given threshold.
func NewPeriodDetector(threshold float64) *PeriodDetector {
	return &PeriodDetector{
		threshold:     threshold,
		listeners:     []EventListener{},
		prevHighStart: time.Time{},
		prevHighEnd:   time.Time{},
		prevHigh:      time.Time{},
		rollingAvg:    streamstat.NewAVG(10),
	}
}

// Update updates the period detector with a new value.
func (p *PeriodDetector) Update(value float64) {
	isNewHighStart := value > p.threshold && p.prevHighStart.IsZero()
	if isNewHighStart {
		p.prevHighStart = time.Now()
		return
	}

	isNewHighEnd := value < p.threshold && p.prevHighEnd.IsZero() && !p.prevHighStart.IsZero()
	if isNewHighEnd {
		p.prevHighEnd = time.Now()
		return
	}

	isNewHigh := !p.prevHighStart.IsZero() && !p.prevHighEnd.IsZero()
	if isNewHigh {
		highDuration := p.prevHighEnd.Sub(p.prevHighStart)
		midpoint := highDuration / 2
		currHigh := p.prevHighStart.Add(midpoint)

		if !p.prevHigh.IsZero() {
			period := currHigh.Sub(p.prevHigh)
			// Check if the period is within the limits
			if p.limit.Min > 0 && period < p.limit.Min {
				p.Reset()
				return
			}
			if p.limit.Max > 0 && period > p.limit.Max {
				p.Reset()
				return
			}

			// Update the rolling average with the new period
			p.rollingAvg.Add(period.Seconds())

			p.periodCount++
			// Notify listeners of the new period only
			// when we are sure that we have recorded enough periods
			// to avoid notifying listeners for the first possibly incorrect period
			if p.periodCount > 1 {
				avgPeriod := time.Duration(int(p.rollingAvg.Get()*1000)) * time.Millisecond
				go p.notifyListeners(avgPeriod)
			}
		}

		p.prevHigh = currHigh
		p.prevHighStart = time.Time{}
		p.prevHighEnd = time.Time{}
	}
}

// Reset resets the period detector state.
func (p *PeriodDetector) Reset() {
	p.prevHighStart = time.Time{}
	p.prevHighEnd = time.Time{}
	p.prevHigh = time.Time{}
	p.periodCount = 0
	p.rollingAvg.Reset()
}

func (p *PeriodDetector) SetLimit(limit PeriodLimit) {
	p.limit = limit
}

// EventListener is a function type for period event listeners.
type EventListener func(period time.Duration)

// AddListener adds a new event listener.
func (p *PeriodDetector) AddListener(listener EventListener) {
	p.listeners = append(p.listeners, listener)
}

// notifyListeners notifies all registered listeners of a new period.
func (p *PeriodDetector) notifyListeners(period time.Duration) {
	for _, listener := range p.listeners {
		listener(period)
	}
}

package waveform

import (
	"log"
	"time"

	"github.com/EelisK/artbit/internal/kernel/streamstat"
)

var logger = log.New(log.Writer(), "waveform: ", log.LstdFlags)

// PeriodDetector is a simple period detector.
type PeriodDetector struct {
	threshold float64

	listeners []EventListener

	prevHighStart time.Time
	prevHighEnd   time.Time
	prevHigh      time.Time

	periodCount uint64

	periodLimit    TimeLimit
	valueLimit     NumericLimit
	amplitudeLimit NumericLimit

	periodAvg   *streamstat.AVG
	valueAvg    *streamstat.AVG
	valueMinMax *streamstat.MinMaxScaler
}

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

func (t TimeLimit) Duration() time.Duration {
	if t.Min > 0 && t.Max > 0 {
		return t.Max - t.Min
	}
	if t.Max > 0 {
		return t.Max
	}
	return t.Min
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

// NewPeriodDetector creates a new PeriodDetector with the given threshold.
func NewPeriodDetector(threshold float64) *PeriodDetector {
	return &PeriodDetector{
		threshold:     threshold,
		listeners:     []EventListener{},
		prevHighStart: time.Time{},
		prevHighEnd:   time.Time{},
		prevHigh:      time.Time{},
		periodAvg:     streamstat.NewAVG(10),
		valueAvg:      streamstat.NewAVG(20),
		valueMinMax:   streamstat.NewMinMaxScaler(1000),
	}
}

// Update updates the period detector with a new value.
func (p *PeriodDetector) Update(value float64) float64 {
	defer p.handlePeriod()
	return p.handleValue(value)
}

// Reset resets the period detector state.
func (p *PeriodDetector) Reset() {
	p.prevHighStart = time.Time{}
	p.prevHighEnd = time.Time{}
	p.prevHigh = time.Time{}
	p.periodCount = 0
	p.periodAvg.Reset()
	p.valueAvg.Reset()
	p.valueMinMax.Reset()
}

func (p *PeriodDetector) SetPeriodLimit(limit TimeLimit) {
	p.periodLimit = limit
}

func (p *PeriodDetector) SetValueLimit(limit NumericLimit) {
	p.valueLimit = limit
}

func (p *PeriodDetector) SetAmplitudeLimit(limit NumericLimit) {
	p.amplitudeLimit = limit
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

func (p *PeriodDetector) handleValue(value float64) float64 {
	// Check if the value is within the value limits
	if !p.valueLimit.IsInRange(value) {
		logger.Printf("Value %.3f is out of range: %v\n", value, p.valueLimit)
		p.Reset()
		return value
	}

	// Update the value transformers
	p.valueAvg.Add(value)

	// Check if the transformers are ready
	if !p.valueAvg.Ready() {
		return value
	}

	// Get the rolling average value
	value = p.valueAvg.Get()

	// Update the min-max scaler
	p.valueMinMax.Add(value)
	if !p.valueMinMax.Ready() {
		return value
	}

	// Check if the value is within the amplitude limits
	if minMaxRange := p.valueMinMax.GetRange(); !p.amplitudeLimit.IsInRange(minMaxRange) {
		logger.Printf(
			"Amplitude range %.3f is out of range: [%v, %v]\n",
			minMaxRange,
			p.amplitudeLimit.Min,
			p.amplitudeLimit.Max,
		)
		p.Reset()
		return value
	}

	// Scale the value to the range [0, 1]
	value = p.valueMinMax.Scale(value)

	// Check if we have entered a new high
	isNewHighStart := value > p.threshold && p.prevHighStart.IsZero()
	if isNewHighStart {
		p.prevHighStart = time.Now()
		return value
	}

	// Check if we have exited a high
	isNewHighEnd := value < p.threshold && p.prevHighEnd.IsZero() && !p.prevHighStart.IsZero()
	if isNewHighEnd {
		p.prevHighEnd = time.Now()
	}

	return value
}

// handlePeriod handles the detection of a new period.
func (p *PeriodDetector) handlePeriod() {
	canDeterminePeriod := !p.prevHighStart.IsZero() && !p.prevHighEnd.IsZero()
	if !canDeterminePeriod {
		return
	}

	highDuration := p.prevHighEnd.Sub(p.prevHighStart)
	midpoint := highDuration / 2
	currHigh := p.prevHighStart.Add(midpoint)

	if !p.prevHigh.IsZero() {
		period := currHigh.Sub(p.prevHigh)
		// Check if the period is within the limits
		if !p.periodLimit.IsInRange(period) {
			logger.Printf(
				"Period of %.3f seconds is out of range: %v\n",
				period.Seconds(),
				p.periodLimit,
			)
			p.Reset()
			return
		}

		// Update the rolling average with the new period
		p.periodAvg.Add(period.Seconds())

		p.periodCount++
		// Notify listeners of the new period only
		// when we are sure that we have recorded enough periods
		// to avoid notifying listeners for the first possibly incorrect period
		if p.periodCount > 1 {
			avgPeriod := time.Duration(int(p.periodAvg.Get()*1000)) * time.Millisecond
			go p.notifyListeners(avgPeriod)
		}
	}

	p.prevHigh = currHigh
	p.prevHighStart = time.Time{}
	p.prevHighEnd = time.Time{}
}

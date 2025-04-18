package kernel

import "time"

type TermUI interface {
	Start() error
	Stop() error
	DrawWavePeriod(period time.Duration) error
	DrawValue(value float64) error
}

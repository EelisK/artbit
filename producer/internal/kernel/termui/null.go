package termui

import "time"

type Null struct{}

func NewNull() *Null                             { return &Null{} }
func (*Null) Start() error                       { return nil }
func (*Null) Stop() error                        { return nil }
func (*Null) DrawWavePeriod(time.Duration) error { return nil }
func (*Null) DrawValue(float64) error            { return nil }

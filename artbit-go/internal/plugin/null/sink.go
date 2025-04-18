package null

type Sink struct{}

func (*Sink) Start() error        { return nil }
func (*Sink) Stop() error         { return nil }
func (*Sink) Write(float64) error { return nil }

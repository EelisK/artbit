package kernel

// Sink is an interface that defines the methods for a data sink.
type Sink interface {
	// Start initializes the sink
	Start() error
	// Stop tears down the sink
	Stop() error
	// Write sends data to the sink
	Write(data float64) error
}

// Source is an interface that defines the methods for a data source.
type Source interface {
	// Start initializes the source
	Start() error
	// Stop tears down the source
	Stop() error
	// Read retrieves data from the source
	Read() (float64, error)
}

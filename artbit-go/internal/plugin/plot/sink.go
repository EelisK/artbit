package plot

import (
	"fmt"
	"io"
	"os"
	"strings"
)

type Sink struct {
	Width  int
	Output io.Writer
}

func NenSink(width int, writer io.Writer) *Sink {
	return &Sink{Width: width, Output: writer}
}

func NewStdout(width int) *Sink {
	return NenSink(width, os.Stdout)
}

func NewStderr(width int) *Sink {
	return NenSink(width, os.Stderr)
}

func (s *Sink) Start() error {
	return nil
}

func (s *Sink) Stop() error {
	if flusher, ok := s.Output.(interface{ Flush() error }); ok {
		return flusher.Flush()
	}
	return nil
}

func (s *Sink) Write(data float64) error {
	pillarCount := int(data * float64(s.Width))
	emptyCount := s.Width - pillarCount
	pillar := strings.Repeat("*", pillarCount) + strings.Repeat(" ", emptyCount)
	output := fmt.Sprintf("%.3f | %s |\n", data, pillar)
	s.Output.Write([]byte(output))
	return nil
}

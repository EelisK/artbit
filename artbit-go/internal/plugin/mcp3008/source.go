package mcp3008

import (
	"gobot.io/x/gobot/drivers/spi"
	"gobot.io/x/gobot/platforms/raspi"
)

const (
	DefaultMCP3008Channel  = 0
	DefaultMCP3008MaxValue = 1023
)

type Source struct {
	MCP3008Channel  int
	MCP3008MaxValue int

	adc  *spi.MCP3008Driver
	conn *raspi.Adaptor
}

func NewSource() *Source {
	conn := raspi.NewAdaptor()
	adc := spi.NewMCP3008Driver(conn)
	return &Source{
		MCP3008Channel:  DefaultMCP3008Channel,
		MCP3008MaxValue: DefaultMCP3008MaxValue,
		adc:             adc,
		conn:            conn,
	}
}

func (s *Source) Start() error {
	if err := s.conn.Connect(); err != nil {
		return err
	}
	if err := s.adc.Start(); err != nil {
		return err
	}
	return nil
}

func (s *Source) Read() (float64, error) {
	result, err := s.adc.Read(s.MCP3008Channel)
	if err != nil {
		return 0.0, err
	}
	return float64(result) / float64(s.MCP3008MaxValue), nil
}

func (s *Source) Stop() error {
	if err := s.adc.Halt(); err != nil {
		return err
	}
	return nil
}

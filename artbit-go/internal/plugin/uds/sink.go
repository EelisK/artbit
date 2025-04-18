package uds

import (
	"fmt"
	"log"
	"net"
	"time"
)

// Unix Domain Socket (UDS) sink
type Sink struct {
	// UDS socket path
	SocketPath string
	// Timeout for sending data
	Timeout time.Duration
	// Connection
	conn net.Conn
	// Channel for sending data
	dataCh chan []byte
	// Channel for stopping the sink
	stopCh chan struct{}
}

var logger = log.New(log.Writer(), "uds-sink: ", log.LstdFlags)

// NewSink creates a new UDS sink
func NewSink(socketPath string, timeout time.Duration) *Sink {
	return &Sink{
		SocketPath: socketPath,
		Timeout:    timeout,
		dataCh:     make(chan []byte),
		stopCh:     make(chan struct{}),
	}
}

// Start starts the UDS sink
func (s *Sink) Start() error {
	logger.Printf("connecting to UDS socket: %s", s.SocketPath)

	connCh := make(chan net.Conn)
	makeConn := func() {
		conn, err := net.Dial("unix", s.SocketPath)
		if err != nil {
			connCh <- nil
			return
		}
		connCh <- conn
	}
	go makeConn()
	select {
	case <-time.After(s.Timeout):
		return fmt.Errorf("timeout connecting to UDS socket: %s", s.SocketPath)
	case conn := <-connCh:
		if conn == nil {
			return fmt.Errorf("failed to connect to UDS socket: %s", s.SocketPath)
		}
		logger.Printf("connected to UDS socket: %s", s.SocketPath)
		s.conn = conn
	}

	go s.sendData()

	return nil
}

// Stop stops the UDS sink
func (s *Sink) Stop() error {
	logger.Printf("stopping UDS sink")
	s.stopCh <- struct{}{}
	defer close(s.dataCh)
	defer close(s.stopCh)
	if s.conn != nil {
		return s.conn.Close()
	}
	return nil
}

// Write writes data to the UDS sink
func (s *Sink) Write(value float64) error {
	// Convert value to byte slice
	data := []byte(fmt.Sprintf("%f\n", value))

	// Send data to the channel
	s.dataCh <- data

	return nil
}

// sendData sends data to the UDS socket
func (s *Sink) sendData() {
	for {
		select {
		case data := <-s.dataCh:
			if err := s.send(data); err != nil {
				panic(err)
			}
		case <-s.stopCh:
			return
		}
	}
}

// send sends data to the UDS socket
func (s *Sink) send(data []byte) error {
	// Set a timeout for sending data
	if err := s.conn.SetWriteDeadline(time.Now().Add(s.Timeout)); err != nil {
		return err
	}

	// Send data to the UDS socket
	_, err := s.conn.Write(data)
	return err
}

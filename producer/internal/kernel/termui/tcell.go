package termui

import (
	"fmt"
	"log"
	"sync"
	"syscall"
	"time"

	tcell "github.com/gdamore/tcell/v2"
)

var logger = log.New(log.Writer(), "termui: ", log.LstdFlags)

type TCell struct {
	screen tcell.Screen
	style  tcell.Style

	graphValues []float64
}

func NewTCell() (*TCell, error) {
	defStyle := tcell.StyleDefault.Background(tcell.ColorReset).Foreground(tcell.ColorReset)

	// Initialize screen
	s, err := tcell.NewScreen()
	if err != nil {
		return nil, err
	}
	if err := s.Init(); err != nil {
		return nil, err
	}

	s.SetStyle(defStyle)

	return &TCell{screen: s, style: defStyle}, nil
}

func (t *TCell) Start() error {
	go func() {
		for {
			ev := t.screen.PollEvent()
			switch ev := ev.(type) {
			case *tcell.EventResize:
				// Resize the screen
				t.screen.Sync()
			case *tcell.EventKey:
				if ev.Key() == tcell.KeyCtrlC || ev.Key() == tcell.KeyEscape {
					t.Stop()
					syscall.Kill(syscall.Getpid(), syscall.SIGINT)
					return
				}
			}
		}
	}()
	t.screen.Clear()
	t.screen.Show()
	return nil
}

func (t *TCell) Stop() error {
	t.screen.Fini()
	return nil
}

func (t *TCell) DrawWavePeriod(period time.Duration) error {
	value := 60 / period.Seconds()
	// Draw period on the top left corner
	for i, char := range fmt.Sprintf("BPM: %.2f", value) {
		t.screen.SetContent(i, 0, char, nil, t.style)
	}
	// Draw a line below the period
	x, _ := t.screen.Size()
	for i := 0; i < x; i++ {
		t.screen.SetContent(i, 1, '-', nil, t.style)
	}
	// Refresh the screen to show changes
	t.screen.Show()
	return nil
}

func (t *TCell) DrawValue(value float64) error {
	// Update graph with the new value
	// Draw the values as vertical pillars from latest to earliest
	// So that the pillar starts from the bottom of the screen and goes down to 10 in the y axis
	x, y := t.screen.Size()

	t.graphValues = append(t.graphValues, value)
	if len(t.graphValues) > x {
		t.graphValues = t.graphValues[1:]
	}
	// backfill with zeros if the graph is not full
	if len(t.graphValues) < x {
		missing := x - len(t.graphValues)
		// Fill the missing values with zeros
		// This is to ensure that the graph is always full
		for i := 0; i < missing; i++ {
			t.graphValues = append(t.graphValues, 0)
		}
	}

	// Start from the bottom of the screen - 2
	pillarStartY := y - 2
	// The end of the pillar is at 10
	pillarEndY := 3
	// The maximum height of the pillar is 10
	pillarMaxHeight := pillarStartY - pillarEndY

	wg := sync.WaitGroup{}
	wg.Add(len(t.graphValues))

	for i, v := range t.graphValues {
		go func(i int, v float64) {
			defer wg.Done()
			pillarX := i
			pillarHeight := int(v * float64(pillarMaxHeight))
			pillarRangeStart := pillarStartY - pillarHeight
			pillarRangeEnd := pillarStartY

			for pillarY := pillarRangeStart; pillarY <= pillarRangeEnd; pillarY++ {
				t.screen.SetContent(pillarX, pillarY, '█', nil, t.style)
			}

			// Clear the area above the pillar
			for pillarY := pillarEndY; pillarY < pillarRangeStart; pillarY++ {
				t.screen.SetContent(pillarX, pillarY, ' ', nil, t.style)
			}
		}(i, v)
	}
	// Wait for all goroutines to finish
	wg.Wait()

	// Refresh the screen to show changes
	t.screen.Show()
	return nil
}

func (t *TCell) clearArea(startX, endX, startY, endY int) {
	for x := startX; x <= endX; x++ {
		for y := startY; y <= endY; y++ {
			t.screen.SetContent(x, y, ' ', nil, tcell.StyleDefault)
		}
	}
}

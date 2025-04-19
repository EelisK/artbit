package streamstat

import (
	"github.com/Workiva/go-datastructures/queue"
	"github.com/gammazero/deque"
)

type Max struct {
	window int
	queue  *queue.RingBuffer
	deque  *deque.Deque[float64]
}

func NewMax(window int) *Max {
	return &Max{
		window: window,
		queue:  queue.NewRingBuffer(uint64(window)),
		deque:  new(deque.Deque[float64]),
	}
}

func (m *Max) Add(x float64) {
	if m.queue.Len() == uint64(m.window) {
		val, err := m.queue.Get()
		if err != nil {
			panic(err)
		}

		if m.deque.Front() == *val.(*float64) {
			m.deque.PopFront()
		}
	}

	err := m.queue.Put(&x)
	if err != nil {
		panic(err)
	}

	for m.deque.Len() > 0 && m.deque.Back() < x {
		m.deque.PopBack()
	}
	m.deque.PushBack(x)
}

func (m *Max) Value() float64 {
	if m.deque.Len() == 0 {
		return 0
	}
	return m.deque.Front()
}

func (m *Max) Reset() {
	m.queue.Dispose()
	m.queue = queue.NewRingBuffer(uint64(m.window))
	m.deque.Clear()
}

func (m *Max) Ready() bool {
	return m.queue.Len() == uint64(m.window)
}

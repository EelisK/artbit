package streamstat

import (
	"testing"
)

func TestWindowedMinMaxScaler(t *testing.T) {
	scaler := NewMinMax(3)

	// Test adding values and scaling
	scaler.Add(10)
	scaler.Add(20)
	scaler.Add(30)

	if got := scaler.Scale(10); got != 0 {
		t.Errorf("Scale(10) = %v; want 0", got)
	}
	if got := scaler.Scale(20); got != 0.5 {
		t.Errorf("Scale(20) = %v; want 0.5", got)
	}
	if got := scaler.Scale(30); got != 1 {
		t.Errorf("Scale(30) = %v; want 1", got)
	}

	// Test sliding window behavior
	scaler.Add(40) // This should remove 10 from the window
	if got := scaler.Scale(20); got != 0 {
		t.Errorf("Scale(20) = %v; want 0", got)
	}
	if got := scaler.Scale(30); got != 0.5 {
		t.Errorf("Scale(30) = %v; want 0.5", got)
	}
	if got := scaler.Scale(40); got != 1 {
		t.Errorf("Scale(40) = %v; want 1", got)
	}

	// Test edge case with all values being the same
	scaler = NewMinMax(3)
	scaler.Add(50)
	scaler.Add(50)
	scaler.Add(50)
	if got := scaler.Scale(50); got != 0.5 {
		t.Errorf("Scale(50) = %v; want 0.5", got)
	}

	// Test resetting the scaler
	scaler = NewMinMax(3)
	scaler.Add(10)
	scaler.Add(20)
	scaler.Add(30)
	scaler.Add(40) // This should remove 10 from the window
	if got := scaler.Scale(20); got != 0 {
		t.Errorf("Scale(20) = %v; want 0", got)
	}
	if got := scaler.Scale(30); got != 0.5 {
		t.Errorf("Scale(30) = %v; want 0.5", got)
	}
	if got := scaler.Scale(40); got != 1 {
		t.Errorf("Scale(40) = %v; want 1", got)
	}
	scaler.Reset()
	scaler.Add(10)
	scaler.Add(20)
	if got := scaler.Scale(10); got != 0 {
		t.Errorf("Scale(10) = %v; want 0", got)
	}
	if got := scaler.Scale(20); got != 1 {
		t.Errorf("Scale(20) = %v; want 1", got)
	}

	// Test empty scaler
	scaler = NewMinMax(3)
	if got := scaler.Scale(10); got != 0.5 {
		t.Errorf("Scale(10) = %v; want 0.5", got)
	}

	// Test random order of values
	scaler = NewMinMax(3)
	scaler.Add(30)
	scaler.Add(10)
	scaler.Add(20)
	if got := scaler.Scale(10); got != 0 {
		t.Errorf("Scale(10) = %v; want 0", got)
	}
	if got := scaler.Scale(20); got != 0.5 {
		t.Errorf("Scale(20) = %v; want 0.5", got)
	}
	if got := scaler.Scale(30); got != 1 {
		t.Errorf("Scale(30) = %v; want 1", got)
	}

	scaler.Add(40) // This should remove 30 from the window
	// Now our range is [10, 40] (range 30)
	// so: scale(10) == 0
	// scale(25) == 0.5
	// scale(40) == 1
	if got := scaler.Scale(10); got != 0 {
		t.Errorf("Scale(20) = %v; want 0", got)
	}
	if got := scaler.Scale(25); got != 0.5 {
		t.Errorf("Scale(20) = %v; want 0.5", got)
	}
	if got := scaler.Scale(40); got != 1 {
		t.Errorf("Scale(20) = %v; want 1", got)
	}
}

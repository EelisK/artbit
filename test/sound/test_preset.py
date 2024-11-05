import numpy as np

from artbit.sound.presets import Silence


def test_silence_duration():
    duration = 2.0
    silence = Silence(duration)

    assert np.all(silence.wave == 0)
    assert silence.get_length() == duration

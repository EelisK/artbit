import pygame
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup_pygame():
    pygame.mixer.init(frequency=44100, size=-16, channels=2)
    yield
    pygame.mixer.quit()

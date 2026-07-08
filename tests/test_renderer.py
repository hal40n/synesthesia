import pygame

from syn.render.renderer import Renderer
from syn.render.state import ColorState


def test_runs_requested_frames_and_shuts_down():
    calls = []

    def next_state():
        calls.append(1)
        return ColorState(hue=200.0, saturation=0.6, brightness=0.8)

    renderer = Renderer(width=320, height=180, fps=120)
    renderer.run(next_state, max_frames=5)

    assert len(calls) == 5
    assert not pygame.get_init()  # cleanly shut down


def test_survives_brightness_extremes():
    states = iter(
        [
            ColorState(hue=0.0, saturation=0.0, brightness=0.0),
            ColorState(hue=359.9, saturation=1.0, brightness=1.0),
            ColorState(hue=180.0, saturation=0.5, brightness=0.5),
        ]
    )
    renderer = Renderer(width=320, height=180, fps=120)
    renderer.run(lambda: next(states), max_frames=3)

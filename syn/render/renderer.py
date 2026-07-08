"""Generative particle renderer.

Visual randomness lives only here: it shapes the pattern, never the
interpretation. Color meaning always comes from the ColorState.
"""

import random

import pygame

from syn.render.state import ColorState, hsv_to_rgb255

MAX_SPAWN_PER_FRAME = 6
HUE_JITTER = 12.0  # degrees of per-particle hue variation


class _Particle:
    def __init__(self, x, y, vx, vy, hue, saturation, brightness, size, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.hue = hue
        self.saturation = saturation
        self.brightness = brightness
        self.size = size
        self.life = life
        self.age = 0.0

    def step(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt

    @property
    def alive(self) -> bool:
        return self.age < self.life

    def color(self) -> tuple[int, int, int]:
        fade = max(0.0, 1.0 - self.age / self.life)
        return hsv_to_rgb255(self.hue, self.saturation, self.brightness * fade)


class Renderer:
    def __init__(self, width: int = 960, height: int = 540, fps: int = 60):
        self.width = width
        self.height = height
        self.fps = fps

    def run(self, next_state, max_frames: int | None = None):
        """Drive the window until quit/ESC (or max_frames, for tests).

        next_state() is called once per frame and must return the
        ColorState to draw.
        """
        pygame.init()
        try:
            screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("syn")
            clock = pygame.time.Clock()
            rng = random.Random()
            particles: list[_Particle] = []

            frames = 0
            running = True
            while running and (max_frames is None or frames < max_frames):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        running = False

                state = next_state()
                dt = 1.0 / self.fps
                self._spawn(particles, state, rng)
                self._draw(screen, particles, state, dt)
                pygame.display.flip()
                clock.tick(self.fps)
                frames += 1
        finally:
            pygame.quit()

    def _spawn(self, particles: list[_Particle], state: ColorState, rng: random.Random):
        expected = state.brightness * MAX_SPAWN_PER_FRAME
        count = int(expected)
        if rng.random() < expected - count:
            count += 1

        cx, cy = self.width / 2.0, self.height / 2.0
        for _ in range(count):
            angle = rng.uniform(0.0, 6.283185)
            speed = rng.uniform(30.0, 120.0) * (0.5 + state.brightness)
            radius = rng.uniform(0.0, self.height * 0.15)
            particles.append(
                _Particle(
                    x=cx + radius * rng.uniform(-1.0, 1.0),
                    y=cy + radius * rng.uniform(-1.0, 1.0),
                    vx=speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x,
                    vy=speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y,
                    hue=state.hue + rng.uniform(-HUE_JITTER, HUE_JITTER),
                    saturation=state.saturation,
                    brightness=min(1.0, 0.4 + 0.6 * state.brightness),
                    size=2.0 + 5.0 * state.brightness,
                    life=rng.uniform(1.0, 2.5),
                )
            )

    def _draw(self, screen, particles: list[_Particle], state: ColorState, dt: float):
        background = hsv_to_rgb255(
            state.hue, state.saturation * 0.6, 0.05 + 0.10 * state.brightness
        )
        screen.fill(background)

        for particle in particles:
            particle.step(dt)
            if particle.alive:
                pygame.draw.circle(
                    screen,
                    particle.color(),
                    (int(particle.x), int(particle.y)),
                    max(1, int(particle.size)),
                )
        particles[:] = [p for p in particles if p.alive]

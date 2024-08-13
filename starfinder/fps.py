import math
from pygame import Surface
from pygame.time import Clock
import pygame

from starfinder.camera import SCREEN_HEIGHT, SCREEN_WIDTH, Camera, HorizontalCoordinates


class Fps:
    def __init__(self):
        self.font = pygame.font.Font(None, 12)

    def render(self, surface: Surface, clock: Clock):
        bottom = 40
        right = 40

        # draw the fps unit label
        unit = self.font.render(
            "FPS",
            True,
            (255, 255, 255),
            None,
        )
        unit_rect = unit.get_rect()
        unit_rect.bottom = SCREEN_HEIGHT - bottom
        unit_rect.right = SCREEN_WIDTH - right

        surface.blit(unit, unit_rect)

        # draw the fps value
        fps = self.font.render(
            f"{math.ceil(clock.get_fps())}",
            True,
            (255, 255, 255),
            None,
        )

        fps_rect = fps.get_rect()
        fps_rect.bottom = unit_rect.bottom
        fps_rect.right = unit_rect.left - 2

        surface.blit(fps, fps_rect)

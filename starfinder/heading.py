import math
import numpy as np
from pygame import Surface
import pygame

from starfinder.camera import SCREEN_WIDTH, Camera
from starfinder.gfx import draw_aa_circle


class Heading:
    def __init__(self):
        font = pygame.font.Font(None, 20)
        self.north_label = font.render("N", True, (255, 255, 255), (0, 0, 0))

    def render(self, camera: Camera, surface: Surface):
        size = 20
        hsize = size // 2
        top = 40
        left = 40

        cx = SCREEN_WIDTH - left - hsize
        cy = top + hsize

        draw_aa_circle(
            surface,
            (255, 255, 255),
            (cx, cy),
            hsize,
            3,
        )

        angle = camera.yaw - math.pi / 2

        north = self.north_label.get_rect()
        north.center = (
            cx + hsize * np.cos(angle),
            cy + hsize * np.sin(angle),
        )
        surface.blit(self.north_label, north)

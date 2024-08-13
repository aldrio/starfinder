import math
import numpy as np
from pygame import Surface
import pygame
from skyfield.units import Angle

from starfinder.camera import Camera, HorizontalCoordinates


class Grid:
    def __init__(
        self,
        font,
        text_color,
        bg_color,
        altitude_step: int = 15,
        azimuth_step: int = 15,
    ):
        self.grid_lines = []
        self.horizon_line = []

        self.direction_surfaces = [
            (0, font.render("North", True, text_color, bg_color)),
            (45, font.render("NE", True, text_color, bg_color)),
            (90, font.render("East", True, text_color, bg_color)),
            (135, font.render("SE", True, text_color, bg_color)),
            (180, font.render("South", True, text_color, bg_color)),
            (225, font.render("SW", True, text_color, bg_color)),
            (270, font.render("West", True, text_color, bg_color)),
            (315, font.render("NW", True, text_color, bg_color)),
        ]

        # latitude lines
        for altitude in range(-90 + altitude_step, 90, altitude_step):
            line = []
            for azimuth in range(0, 360 + azimuth_step, azimuth_step):
                hc = HorizontalCoordinates(
                    altitude=Angle(
                        degrees=altitude,
                    ),
                    azimuth=Angle(
                        degrees=azimuth,
                    ),
                )
                line.append(
                    np.array(
                        [
                            math.sin(hc.azimuth.radians)
                            * math.cos(-hc.altitude.radians),
                            math.sin(-hc.altitude.radians),
                            math.cos(hc.azimuth.radians)
                            * math.cos(-hc.altitude.radians),
                        ]
                    )
                )

            if altitude == 0:
                self.horizon_line = line
            else:
                self.grid_lines.append(line)

        # longitude lines
        for azimuth in range(0, 360 + azimuth_step, azimuth_step):
            line = []
            for altitude in range(-90 + altitude_step, 90, altitude_step):
                hc = HorizontalCoordinates(
                    altitude=Angle(
                        degrees=altitude,
                    ),
                    azimuth=Angle(
                        degrees=azimuth,
                    ),
                )
                line.append(
                    np.array(
                        [
                            math.sin(hc.azimuth.radians)
                            * math.cos(-hc.altitude.radians),
                            math.sin(-hc.altitude.radians),
                            math.cos(hc.azimuth.radians)
                            * math.cos(-hc.altitude.radians),
                        ]
                    )
                )
            self.grid_lines.append(line)

    def render(self, camera: Camera, surface: Surface):
        # continuous lines in the view
        lines = []
        for grid_line in self.grid_lines:
            lines.extend(get_continuous_lines(grid_line, camera))

        for line in lines:
            if len(line) < 2:
                continue

            pygame.draw.lines(surface, (30, 30, 30), False, line)

        # horizon line
        lines = get_continuous_lines(self.horizon_line, camera)
        for line in lines:
            if len(line) < 2:
                continue

            pygame.draw.lines(surface, (60, 60, 60), False, line, 2)

        # Render direction labels
        for angle, text_surface in self.direction_surfaces:
            point = camera.project(HorizontalCoordinates(azimuth=Angle(degrees=angle)))
            if point:
                text_rect = text_surface.get_rect().inflate(8, 8)
                text_rect.center = point.to_tuple()
                surface.blit(text_surface, text_rect)


def get_continuous_lines(line, camera):
    lines = []
    last_point = None
    for grid_point in line:
        point = camera.project_point(
            grid_point,
        )

        if last_point is None:
            lines.append([])

        last_point = point

        if point is None:
            continue

        lines[-1].append(point.to_tuple())

    return lines

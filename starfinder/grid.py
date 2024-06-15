import math
import numpy as np
from pygame import Surface
import pygame
from skyfield.units import Angle

from starfinder.camera import Camera, HorizontalCoordinates


class Grid:
    def __init__(self, altitude_step: int = 15, azimuth_step: int = 15):
        self.grid_lines = []

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
            last_point = None
            for grid_point in grid_line:
                point = camera.project_point(
                    grid_point,
                )

                if last_point is None:
                    lines.append([])

                last_point = point

                if point is None:
                    continue

                lines[-1].append(point.to_tuple())

        for line in lines:
            if len(line) < 2:
                continue

            pygame.draw.lines(
                surface,
                (30, 30, 30),
                False,
                line,
            )

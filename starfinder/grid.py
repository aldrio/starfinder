import itertools
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
        self.altitude_line_count = int(180 / altitude_step) - 1
        self.azimuth_line_count = int(360 / azimuth_step)

        self.grid_points = []
        self.horizon_points = []

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

        # Generate grid points
        total_altitude = 0
        for altitude in range(-90 + altitude_step, 90, altitude_step):
            total_azimuth = 0
            total_altitude += 1
            for azimuth in range(0, 360, azimuth_step):
                total_azimuth += 1
                hc = HorizontalCoordinates(
                    altitude=Angle(
                        degrees=altitude,
                    ),
                    azimuth=Angle(
                        degrees=azimuth,
                    ),
                )
                point = np.array(
                    [
                        math.sin(hc.azimuth.radians) * math.cos(-hc.altitude.radians),
                        math.sin(-hc.altitude.radians),
                        math.cos(hc.azimuth.radians) * math.cos(-hc.altitude.radians),
                    ]
                )

                self.grid_points.append(point)
                if altitude == 0:
                    self.horizon_points.append(point)

        self.grid_points = np.array(self.grid_points)
        self.horizon_points = np.array(self.horizon_points)

    def render(self, camera: Camera, surface: Surface):
        # continuous lines in the view
        all_projected_points, valid_points_mask = camera.project_points(
            self.grid_points
        )

        for altitude_line_index in range(self.altitude_line_count):
            altitude_line_index_start = altitude_line_index * self.azimuth_line_count
            altitude_line_index_end = (
                altitude_line_index + 1
            ) * self.azimuth_line_count

            altitude_line_points = all_projected_points[
                altitude_line_index_start:altitude_line_index_end
            ]
            valid_altitude_line_points = valid_points_mask[
                altitude_line_index_start:altitude_line_index_end
            ]

            render_valid_lines(
                altitude_line_points,
                valid_altitude_line_points,
                surface,
                wrap=True,
            )

        for azimuth_line_index in range(self.azimuth_line_count):
            azimuth_line_points = all_projected_points[
                azimuth_line_index :: self.azimuth_line_count
            ]
            valid_azimuth_line_points = valid_points_mask[
                azimuth_line_index :: self.azimuth_line_count
            ]

            render_valid_lines(
                azimuth_line_points,
                valid_azimuth_line_points,
                surface,
                wrap=False,
            )

        # Render direction labels
        for angle, text_surface in self.direction_surfaces:
            point = camera.project(HorizontalCoordinates(azimuth=Angle(degrees=angle)))
            if point:
                text_rect = text_surface.get_rect().inflate(8, 8)
                text_rect.center = point.to_tuple()
                surface.blit(text_surface, text_rect)


def pairwise_circle(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ... (s<last>,s0)"
    a, b = itertools.tee(iterable)
    first_value = next(b, None)
    return itertools.zip_longest(a, b, fillvalue=first_value)


def render_valid_lines(
    points: np.ndarray,
    valid_points_mask: np.ndarray,
    surface: Surface,
    wrap: bool = False,
):
    lines = zip(points, valid_points_mask)
    if wrap:
        lines = pairwise_circle(lines)
    else:
        lines = itertools.pairwise(lines)

    for (a_point, a_valid), (b_point, b_valid) in lines:
        if not a_valid or not b_valid:
            continue
        pygame.draw.aaline(surface, (255, 255, 255), a_point[:2], b_point[:2])

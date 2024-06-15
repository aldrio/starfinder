from dataclasses import dataclass
import math
from typing import Optional
from skyfield.units import Angle

import numpy as np


SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
HALF_SCREEN_WIDTH = SCREEN_WIDTH / 2
HALF_SCREEN_HEIGHT = SCREEN_HEIGHT / 2
ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT

PHYSICAL_FOV = math.radians(17.58)


@dataclass
class HorizontalCoordinates:
    altitude: Angle = Angle(degrees=0)
    azimuth: Angle = Angle(degrees=0)


@dataclass
class ScreenPoint:
    x: int
    y: int

    def to_tuple(self) -> tuple[int, int]:
        return self.x, self.y


@dataclass
class Camera:
    pitch: float
    yaw: float
    roll: float
    fov: float

    def __post_init__(self):
        # calculate the rotation matrix
        yaw_matrix = np.array(
            [
                [math.cos(self.yaw), 0, math.sin(self.yaw)],
                [0, 1, 0],
                [-math.sin(self.yaw), 0, math.cos(self.yaw)],
            ]
        )

        pitch_matrix = np.array(
            [
                [1, 0, 0],
                [0, math.cos(self.pitch), -math.sin(self.pitch)],
                [0, math.sin(self.pitch), math.cos(self.pitch)],
            ]
        )

        roll_matrix = np.array(
            [
                [math.cos(self.roll), -math.sin(self.roll), 0],
                [math.sin(self.roll), math.cos(self.roll), 0],
                [0, 0, 1],
            ]
        )

        # Apply rotations in yaw-pitch-roll order
        self.transformation_matrix = np.dot(
            np.dot(
                roll_matrix,
                pitch_matrix,
            ),
            yaw_matrix,
        )
        self.inv_transformation_matrix = np.linalg.inv(self.transformation_matrix)

    def project(self, hc: HorizontalCoordinates) -> Optional[ScreenPoint]:
        """
        Project a ray to a screen pixel
        """

        poi = np.array(
            [
                math.sin(hc.azimuth.radians) * math.cos(-hc.altitude.radians),
                math.sin(-hc.altitude.radians),
                math.cos(hc.azimuth.radians) * math.cos(-hc.altitude.radians),
            ]
        )
        poi /= np.linalg.norm(poi)

        return self.project_point(poi)

    def project_point(self, poi) -> Optional[ScreenPoint]:
        """
        Project a ray to a screen pixel
        """

        # rotate the poi relative to the camera
        poi = np.dot(self.transformation_matrix, poi)

        # don't show things behind the camera
        if poi[2] < 0:
            return None

        # scale to the fov
        poi *= math.pi / self.fov

        return ScreenPoint(
            (poi[0] * HALF_SCREEN_WIDTH) + HALF_SCREEN_WIDTH,
            (poi[1] * HALF_SCREEN_HEIGHT * ASPECT_RATIO) + HALF_SCREEN_HEIGHT,
        )

    def project_angle(self, length: Angle) -> float:
        """
        Project a degree length to a screen length
        """

        # screen width is 180 degrees * math.pi / fov
        # length is in degrees

        return (length.degrees / 180) * (math.pi / self.fov) * SCREEN_WIDTH

    def inverse_project(self, sp: ScreenPoint) -> Optional[HorizontalCoordinates]:
        """
        Project a screen pixel back to a ray in the sky
        """
        # Convert screen coordinates back to normalized device coordinates
        x_ndc = (sp.x - HALF_SCREEN_WIDTH) / HALF_SCREEN_WIDTH
        y_ndc = (sp.y - HALF_SCREEN_HEIGHT) / (
            HALF_SCREEN_HEIGHT * SCREEN_WIDTH / SCREEN_HEIGHT
        )

        # Adjust for field of view
        x_ndc *= self.fov / math.pi
        y_ndc *= self.fov / math.pi
        z_ndc = max(0.0, math.cos(x_ndc) * math.cos(y_ndc))

        # Create a point
        poi = np.array([x_ndc, y_ndc, z_ndc])

        # Apply the inverse of the camera's transformation matrix to get the world coordinates
        poi = np.dot(np.linalg.inv(self.transformation_matrix), poi)

        # Normalize the poi
        poi /= np.linalg.norm(poi)

        # Calculate altitude and azimuth from the poi
        altitude = math.asin(-poi[1])
        azimuth = math.atan2(poi[0], poi[2])

        # Return the horizontal coordinates
        return HorizontalCoordinates(
            altitude=Angle(radians=altitude), azimuth=Angle(radians=azimuth)
        )

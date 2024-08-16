from dataclasses import dataclass
from pygame import Surface
import pygame
from skyfield.units import Angle

from starfinder.camera import Camera, HorizontalCoordinates


@dataclass
class Body:
    name: str
    coordinates: HorizontalCoordinates
    diameter: float
    label: Surface
    color: tuple[int, int, int] = (255, 255, 255)
    in_solar_system: bool = False


class Bodies:
    def __init__(self, eph, observer):
        font = pygame.font.Font(None, 24)

        self.bodies = []

        for key, name, color in [
            ("sun", "Sun", (255, 255, 240)),
            ("moon", "Moon", (255, 255, 250)),
            ("mercury", "Mercury", (250, 250, 250)),
            ("venus", "Venus", (250, 250, 250)),
            ("mars", "Mars", (255, 250, 250)),
            ("jupiter barycenter", "Jupiter", (251, 237, 185)),
            ("saturn barycenter", "Saturn", (255, 248, 233)),
            ("uranus barycenter", "Uranus", (233, 255, 255)),
            ("neptune barycenter", "Neptune", (233, 255, 250)),
            ("pluto barycenter", "Pluto", (255, 248, 233)),
        ]:
            p = eph[key]
            astrometric = observer.observe(p)
            alt, az, d = astrometric.apparent().altaz()

            diameter = Angle(degrees=0.01)
            if key == "sun":
                diameter = Angle(degrees=0.5)
            elif key == "moon":
                diameter = Angle(degrees=0.5)

            self.bodies.append(
                Body(
                    name=name,
                    coordinates=HorizontalCoordinates(
                        altitude=alt,
                        azimuth=az,
                    ),
                    diameter=diameter,
                    label=font.render(
                        name,
                        True,
                        (255, 255, 255),
                    ),
                    color=color,
                    in_solar_system=True,
                )
            )

    def render(self, camera: Camera, surface: Surface):
        for body in self.bodies:
            pos = camera.project(body.coordinates)
            if not pos:
                continue

            # calculate the diameter of the body
            diameter = camera.project_angle(body.diameter)
            diameter = max(1, diameter)

            # increase diameter so it's more visible
            if body.in_solar_system:
                diameter *= 5

            # render body
            pygame.draw.circle(
                surface,
                body.color,
                pos.to_tuple(),
                diameter / 2,
            )

            # render label under the body
            label = body.label.get_rect()
            label.centerx = pos.x
            label.top = pos.y + diameter / 2.0 + 6

            surface.blit(body.label, label)

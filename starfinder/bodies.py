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


class Bodies:
    def __init__(self, eph, observer):
        font = pygame.font.Font(None, 24)

        self.bodies = []

        for key, name in [
            ("sun", "Sun"),
            ("moon", "Moon"),
            ("mercury", "Mercury"),
            ("venus", "Venus"),
            ("mars", "Mars"),
            ("jupiter barycenter", "Jupiter"),
            ("saturn barycenter", "Saturn"),
            ("uranus barycenter", "Uranus"),
            ("neptune barycenter", "Neptune"),
            ("pluto barycenter", "Pluto"),
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
                )
            )

    def render(self, camera: Camera, surface: Surface):
        for body in self.bodies:
            p = camera.project(body.coordinates)
            if not p:
                continue
            pos = p.to_tuple()

            # calculate the diameter of the body
            diameter = camera.project_angle(body.diameter)
            diameter = max(1, diameter)

            # increase diameter so it's more visible
            diameter *= 5

            # render body
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                pos,
                diameter / 2,
            )

            # render label under the body
            label = body.label.get_rect()
            label.centerx = pos[0]
            label.top = pos[1] + diameter / 2.0 + 6

            surface.blit(body.label, label)

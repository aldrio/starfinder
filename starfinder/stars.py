from dataclasses import dataclass
from typing import Optional
from pygame import Surface
import pandas as pd
import pygame
from skyfield.units import Angle, Distance
from skyfield.api import Star

from starfinder.camera import Camera, HorizontalCoordinates


@dataclass
class IndividualStar:
    name: str
    coordinates: HorizontalCoordinates
    diameter: float
    label: Optional[Surface]


class Stars:
    def __init__(self, hpc, observer):
        font = pygame.font.Font(None, 32)

        # ignore NaN values in the hipparcos data
        # (https://rhodesmill.org/skyfield/stars.html#stars-with-nan-positions)
        hpc = hpc[hpc["ra_degrees"].notnull()]

        # order by brightness
        hpc = hpc.sort_values(by="magnitude")

        self.stars = []

        # show brightest stars (and Blaze Star)
        brightest = hpc.head(100)

        # show other stars of interest
        other = hpc[hpc.index.isin([78322])]


        hpc = pd.concat([brightest, other])
        hpc_stars = Star.from_dataframe(hpc)

        alts, azs, ds = observer.observe(hpc_stars).apparent().altaz()

        for hip, alt, az, d in zip(hpc.index, alts.degrees, azs.degrees, ds.km):
            alt = Angle(degrees=alt)
            az = Angle(degrees=az)
            d = Distance(km=d)

            diameter = Angle(degrees=0.01)

            label = None
            if hip == 11767:
                label = "Polaris"
            elif hip == 69673:
                label = "Arcturus"
            elif hip == 91262:
                label = "Vega"
            elif hip == 78322:
                label = "Blaze Star"

            if label:
                label = font.render(label, True, (255, 255, 255))

            self.stars.append(
                IndividualStar(
                    name="Star",
                    coordinates=HorizontalCoordinates(
                        altitude=alt,
                        azimuth=az,
                    ),
                    diameter=diameter,
                    label=label,
                )
            )

    def render(self, camera: Camera, surface: Surface):
        for body in self.stars:
            pos = camera.project(body.coordinates)
            if not pos:
                continue

            # calculate the diameter of the body
            diameter = camera.project_angle(body.diameter)
            diameter = max(1, diameter)

            # increase diameter so it's more visible
            diameter *= 5

            # render body
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                pos.to_tuple(),
                diameter / 2,
            )

            # render label under the body
            if body.label:
                label = body.label.get_rect()
                label.centerx = pos.x
                label.top = pos.y + diameter / 2.0 + 6

                surface.blit(body.label, label)

import math
import pygame
from skyfield.units import Angle
from skyfield.api import load, N, E, wgs84


from starfinder.bodies import Bodies
from starfinder.camera import (
    PHYSICAL_FOV,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    Camera,
    HorizontalCoordinates,
)
from starfinder.fps import Fps
from starfinder.gps import GpsManager
from starfinder.grid import Grid
from starfinder.imu import ImuManager
from starfinder.heading import Heading


def main():
    gps = GpsManager()
    imu = ImuManager()

    # Load the star data
    eph = load("de421.bsp")
    earth = eph["earth"]

    # location
    ts = load.timescale()
    t = ts.now()

    location = gps.get_location(timeout=0.1)
    location = earth + wgs84.latlon(location[0] * N, location[1] * E)
    observer = location.at(t)

    # Initialize Pygame
    pygame.init()

    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Starfinder")

    # Set up the clock
    clock = pygame.time.Clock()

    # Define font and colors
    font = pygame.font.Font(None, 36)
    text_color = (255, 255, 255)
    bg_color = (0, 0, 0)

    # camera = Camera(0, math.radians(180), 0, math.radians(90))
    camera = Camera(0, math.radians(180), 0, PHYSICAL_FOV)

    north_surface = font.render("North", True, text_color, bg_color)
    south_surface = font.render("South", True, text_color, bg_color)

    grid = Grid()
    heading = Heading()
    bodies = Bodies(eph, observer)
    fps = Fps()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    dx, dy = event.rel
                    camera = Camera(
                        camera.pitch - math.radians(dy) / 2,
                        camera.yaw + math.radians(dx) / 2,
                        camera.roll,
                        camera.fov,
                    )

        if imu.running:
            orientation = imu.get_orientation()
            camera = Camera(
                orientation.pitch,
                orientation.yaw,
                -orientation.roll,
                camera.fov,
            )

        # Clear the screen
        screen.fill((0, 0, 0))

        grid.render(camera, screen)
        bodies.render(camera, screen)

        # Render North and South text
        point = camera.project(HorizontalCoordinates(azimuth=Angle(degrees=180)))
        if point:
            text_rect = south_surface.get_rect().inflate(8, 8)
            text_rect.center = point.to_tuple()
            screen.blit(south_surface, text_rect)

        point = camera.project(HorizontalCoordinates(azimuth=Angle(degrees=0)))
        if point:
            text_rect = north_surface.get_rect().inflate(8, 8)
            text_rect.center = point.to_tuple()
            screen.blit(north_surface, text_rect)

        heading.render(camera, screen)
        fps.render(screen, clock)

        # Update the display
        pygame.display.flip()
        clock.tick(60)

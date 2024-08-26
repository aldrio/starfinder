import math
import pygame
import os
import atexit
import time

from skyfield.api import load, N, E, wgs84
from skyfield.data import hipparcos

from starfinder.bodies import Bodies
from starfinder.camera import (
    PHYSICAL_FOV,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    Camera,
)
from starfinder.fps import Fps
from starfinder.gps import GpsManager
from starfinder.grid import Grid
from starfinder.imu import ImuManager
from starfinder.heading import Heading
from starfinder.stars import Stars

# Check if we are running on the device
IS_ON_DEVICE = os.path.exists("/dev/fb1")

# Open the framebuffer if we're on the device
# on the pi, we write directly to the framebuffer to avoid the overhead of X11.
# I had trouble getting pygame/SDL to work with directfb or fbdev, so this is a
# workaround.
if IS_ON_DEVICE:
    fb = open("/dev/fb1", "wb")
    atexit.register(fb.close)


class Main:

    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up display
        if IS_ON_DEVICE:
            self.screen = pygame.surface.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 16)
        else:
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                vsync=False,
            )
            pygame.display.set_caption("Starfinder")

        # Define font and colors
        self.font = pygame.font.Font(None, 36)
        self.text_color = (255, 255, 255)
        self.bg_color = (0, 0, 0)

        # Set up the clock
        self.clock = pygame.time.Clock()
        self.delta = 0

        self.display_progress(0)

        # Initialize GPS and IMU
        self.gps = GpsManager()
        self.imu = ImuManager()

        # Load the star data
        self.eph = load("de421.bsp")

        with load.open(hipparcos.URL) as f:
            self.hpc = hipparcos.load_dataframe(f)

        self.coordinates = None
        self.last_location_update = 0
        self.update_location()
        self.prepare_info()

        # self.camera = Camera(0, math.radians(180), 0, math.radians(60))
        self.camera = Camera(0, math.radians(180), 0, math.radians(60))

        self.grid = Grid(self.font, self.text_color, self.bg_color)
        self.heading = Heading()
        self.fps = Fps()

        while True:
            self.tick_input()
            self.render()
            self.delta = self.clock.tick(30) / 1000

    def tick_input(self):
        """
        Handle input events
        """

        # Get window events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    dx, dy = event.rel
                    self.camera = Camera(
                        self.camera.pitch - math.radians(dy) / 2,
                        self.camera.yaw + math.radians(dx) / 2,
                        self.camera.roll,
                        self.camera.fov,
                    )

        # Update the camera orientation from the IMU
        if self.imu.running:
            orientation = self.imu.get_orientation()

        # Update the GPS
        if time.monotonic() - self.last_location_update > 15:
            self.update_location()

    def render(self):
        """
        Render the scene
        """

        # Clear the screen
        self.screen.fill((0, 0, 0))

        # Render
        self.grid.render(self.camera, self.screen)
        self.stars.render(self.camera, self.screen)
        self.bodies.render(self.camera, self.screen)
        self.fps.render(self.screen, self.clock)
        self.heading.render(self.camera, self.screen)

        # Update the display
        self.refresh()

    def update_location(self):
        """
        Update the observer's location
        """

        self.last_location_update = time.monotonic()
        coordinates = self.gps.get_location(timeout=0.1)

        if self.coordinates is None:
            coordinates_diff = math.inf
        else:
            coordinates_diff = math.sqrt(
                (coordinates[0] - self.coordinates[0]) ** 2
                + (coordinates[1] - self.coordinates[1]) ** 2
            )

        # Update and prepare info if the location has changed significantly
        if coordinates_diff > 1.0:
            self.coordinates = coordinates
            self.prepare_info()

    def prepare_info(self):
        """
        Load the data for display
        """

        earth = self.eph["earth"]

        # location
        ts = load.timescale()
        t = ts.now()

        location = earth + wgs84.latlon(
            self.coordinates[0] * N,
            self.coordinates[1] * E,
        )
        observer = location.at(t)

        self.bodies = Bodies(self.eph, observer)
        self.stars = Stars(self.hpc, observer)

    def display_progress(self, pct):
        """
        Render the loading screen
        """

        # TODO: loading progress?
        text = self.font.render("Loading...", True, self.text_color, self.bg_color)
        text_rect = text.get_rect()
        text_rect.center = self.screen.get_rect().center
        self.screen.blit(text, text_rect)

        # Update the display
        self.refresh()

    def refresh(self):
        if IS_ON_DEVICE:
            fb.seek(0)
            fb.write(self.screen.get_buffer())
            fb.flush()
        else:
            pygame.display.flip()

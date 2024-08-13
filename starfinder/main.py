import math
import pygame
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


class Main:

    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Starfinder")

        # Define font and colors
        self.font = pygame.font.Font(None, 36)
        self.text_color = (255, 255, 255)
        self.bg_color = (0, 0, 0)

        # Set up the clock
        self.clock = pygame.time.Clock()

        self.display_progress(0)

        # Initialize GPS and IMU
        self.gps = GpsManager()
        self.imu = ImuManager()

        # Load the star data
        self.eph = load("de421.bsp")

        with load.open(hipparcos.URL) as f:
            self.hpc = hipparcos.load_dataframe(f)

        self.prepare_info()

        # self.camera = Camera(0, math.radians(180), 0, math.radians(60))
        self.camera = Camera(0, math.radians(180), 0, PHYSICAL_FOV)

        self.grid = Grid(self.font, self.text_color, self.bg_color)
        self.heading = Heading()
        self.fps = Fps()

        while True:
            self.tick_input()
            self.render()
            self.clock.tick(60)

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
            self.camera = Camera(
                orientation.pitch,
                orientation.yaw,
                -orientation.roll,
                self.camera.fov,
            )

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
        pygame.display.flip()

    def prepare_info(self):
        """
        Load the data for display
        """

        earth = self.eph["earth"]

        # location
        ts = load.timescale()
        t = ts.now()

        location = self.gps.get_location(timeout=0.1)
        location = earth + wgs84.latlon(location[0] * N, location[1] * E)
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
        pygame.display.flip()

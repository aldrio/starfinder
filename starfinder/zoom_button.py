import time
from typing import Optional
import pygame
from gpiozero import Button


class ZoomButton:
    def __init__(
        self,
        pygame_key: int,
        physical_button: Optional[Button],
        on_single_press: Optional[callable],
        on_double_press: Optional[callable],
    ):
        self.pygame_key = pygame_key
        self.physical_button = physical_button
        self.on_single_press = on_single_press
        self.on_double_press = on_double_press

        # manage state
        self.pressed_at = None

        self.is_double = False
        self.last_short_press_at = None

        self.long_pressed = False

        self.long_press_time = 0.2
        self.double_press_time = 1

    def handle_event(self, event: pygame.event.Event):
        """
        Handle pygame events for this button
        """

        if event.type == pygame.KEYDOWN and event.key == self.pygame_key:
            self.down()
        elif event.type == pygame.KEYUP and event.key == self.pygame_key:
            self.up()

    def poll(self):
        """
        Poll the physical button
        """

        if self.physical_button is None:
            return

        is_pressed = self.physical_button.is_pressed
        if is_pressed and not self.pressed_at:
            self.down()
        elif not is_pressed and self.pressed_at:
            self.up()

    def update(self):
        """
        Update the state of the button
        """

        now = time.monotonic()
        if self.pressed_at and now - self.pressed_at > self.long_press_time:
            self.long_pressed = True
        else:
            self.long_pressed = False

    def down(self):
        now = time.monotonic()

        self.pressed_at = now
        self.long_pressed = False

        if (
            self.last_short_press_at is not None
            and now - self.last_short_press_at < self.double_press_time
        ):
            self.is_double = True
            self.last_short_press_at = None
        else:
            self.is_double = False

    def up(self):
        if not self.pressed_at:
            return

        now = time.monotonic()

        press_time = now - self.pressed_at
        self.pressed_at = None

        if press_time < self.long_press_time:

            if self.is_double:
                self.double()
            else:
                self.last_short_press_at = now
                self.single()

    def single(self):
        if self.on_single_press:
            self.on_single_press()

    def double(self):
        if self.on_double_press:
            self.on_double_press()

    @property
    def is_zooming(self):
        return self.long_pressed

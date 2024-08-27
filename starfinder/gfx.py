"""
Some improved drawing functions
"""

import math
import pygame
import pygame.gfxdraw


def draw_aa_circle(
    surface: pygame.Surface,
    color,
    center,
    radius: int,
    width: int = 1,
):
    """
    An anti-aliased circle/ring
    """
    target = pygame.surface.Surface(
        (radius * 2 + 2, radius * 2 + 2),
        pygame.SRCCOLORKEY,
    )
    hw = target.get_width() // 2
    hh = target.get_height() // 2
    bg = (0, 0, 0)
    target.set_colorkey(bg)

    # Draw the circle
    draw_aa_filled_circle(
        target,
        color,
        (hw, hh),
        radius,
    )

    # Erase the inner circle to make it hollow
    draw_aa_filled_circle(
        target,
        bg,
        (hw, hh),
        radius - width,
    )

    surface.blit(
        target,
        (
            center[0] - hw,
            center[1] - hh,
        ),
    )


def draw_aa_filled_circle(
    surface: pygame.Surface,
    color,
    center,
    radius: int,
):
    """
    An anti-aliased filled circle
    """
    x = math.floor(center[0])
    y = math.floor(center[1])

    # Draw the circle antialiased outline
    pygame.gfxdraw.aacircle(
        surface,
        x,
        y,
        int(radius),
        color,
    )

    # Fill in the circle
    pygame.gfxdraw.filled_circle(
        surface,
        x,
        y,
        int(radius),
        color,
    )

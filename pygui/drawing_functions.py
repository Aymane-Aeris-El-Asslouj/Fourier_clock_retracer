from utility_functions import geometrical_functions as g_f

import pygame
import math

ARROW_HEAD_SIZE = 15


def draw_arrow(surface, object_origin, map_vector, color, size):
    """Draw an arrow starting at an object origin
    and guided by a map vector"""

    if not g_f.non_zero_2d_vec(map_vector):
        return

    # shortcuts
    origin = object_origin
    scale = g_f.scale_vector
    sub = g_f.sub_vectors
    add = g_f.add_vectors

    L = ARROW_HEAD_SIZE*size
    h = ARROW_HEAD_SIZE*size

    len_v = g_f.norm(map_vector)

    # check that the arrow size is non-zero
    if len_v > 0:

        # get point to which the arrow head should be pointing
        map_vector = scale(map_vector, 1)

        # get unit vectors in the direction
        # and perpendicular to the arrow
        unit = g_f.unit_vector(map_vector)
        perp = g_f.rotate_vector(unit, math.pi/2)

        # scale those unit vectors by arrow dimensions
        new_unit = scale(unit, L)
        new_perp = scale(perp, h)

        # get endpoint of arrow head
        end = add(origin, map_vector)

        # sides of arrow head
        left = add(sub(end, new_unit), new_perp)
        right = sub(sub(end, new_unit), new_perp)

        # draw arrow body and head
        pygame.draw.line(surface, color,
                         origin, end, width=max(1, int(5*size)))
        points = [left, right, end]
        pygame.draw.polygon(surface, color, points)

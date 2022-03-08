import pygame
from pygui import colors as col
from crisnian_code import layer_utilities as l_u
from utility_functions import geometrical_functions as g_f
import colorsys

RED = col.RED
BLUE = col.BLUE


class Manual:
    """stores manual drawing"""

    def __init__(self, layer, size, alpha):
        self._layer = layer
        self._size = size[1], size[1]
        self._drawing = pygame.Surface(size, pygame.SRCALPHA)
        self._alpha = alpha
        self._rgb_font = ((0, 0, 0), 5)
        self._hsv_font = ((0, 0, 0), 5)
        self._point_list = []
        self._animation = None
        self._showing = True
        self._erasing = False
        self._drawing.set_alpha(self._alpha)

    def reset(self):
        """resets the drawing"""

        self._drawing = pygame.Surface(self._size, pygame.SRCALPHA)
        self._drawing.set_alpha(self._alpha)

    def clear(self):
        """clears manual drawing"""

        if self._animation.is_rendering()\
                or self._layer.file_manager.is_exporting():
            return

        self._animation.update_time()
        self.reset()
        self._point_list.clear()
        self._animation.no_render()

    def show(self):
        """toggle showing manual drawing"""
        
        if self._showing:
            self._showing = False
        else:
            self._showing = True

    def erase(self):
        """toggle erasing mode"""
        
        if self._erasing:
            self._erasing = False
        else:
            self._erasing = True

    def update_drawing(self):
        """updates manual drawing board by adding a new point"""

        if len(self._point_list) > 1:
            if l_u.c_mod(self._point_list[-1][0]-self._point_list[-2][0]) < 2:
                new_point = l_u.complex_to_board(self._size,
                                                 self._point_list[-1][0])
                old_point = l_u.complex_to_board(self._size,
                                                 self._point_list[-2][0])
                font = self._point_list[-1][1]
                pygame.draw.line(self._drawing, font[0], old_point,
                                 new_point, font[1])

    def full_redraw(self):
        """fully redrawn the manual drawing"""

        self.reset()

        first = True

        # draw line from previous to next point for all
        # manual points with appropriate font
        for point, font in self._point_list:
            if not first:
                if l_u.c_mod(point - last_point) < 2:
                    new_p = l_u.complex_to_board(self._size, point)
                    old_p = l_u.complex_to_board(self._size, last_point)
                    pygame.draw.line(self._drawing, font[0],
                                     old_p, new_p, font[1])

            first = False
            last_point = point

    def expand(self, point_array):
        """extends the point list with a point array"""

        fonts = [self._rgb_font] * len(point_array)
        self._point_list.extend(zip(point_array, fonts))
        self.update_drawing()

    def increment(self, point):
        """extends the point list with a new point"""

        self._point_list.append((point, self._rgb_font))
        self.update_drawing()

    def __getitem__(self, key):
        """point getter"""

        return self._point_list[key]
    
    def animation(self, animation):
        """setter"""
        
        self._animation = animation
        
    def is_showing(self):
        """getter"""
        
        return self._showing
    
    def is_erasing(self):
        """getter"""
        
        return self._erasing

    def drawing(self):
        """getter"""
        
        return self._drawing

    def set_hue(self, hue):
        """changes font color hue"""

        hsv = self._hsv_font
        self._hsv_font = (min(1, max(0, hue)), hsv[0][1], hsv[0][2]), hsv[1]
        norm_col = colorsys.hsv_to_rgb(*self._hsv_font[0])
        color = g_f.scale_vector(norm_col, 255)
        self._rgb_font = color, self._rgb_font[1]

    def set_sat(self, sat):
        """changes font color saturation"""

        hsv = self._hsv_font
        self._hsv_font = (hsv[0][0], min(1, max(0, sat)), hsv[0][2]), hsv[1]
        norm_col = colorsys.hsv_to_rgb(*self._hsv_font[0])
        color = g_f.scale_vector(norm_col, 255)
        self._rgb_font = color, self._rgb_font[1]

    def set_val(self, val):
        """changes font color value"""

        hsv = self._hsv_font
        self._hsv_font = (hsv[0][0], hsv[0][1], min(1, max(0, val))), hsv[1]
        norm_col = colorsys.hsv_to_rgb(*self._hsv_font[0])
        color = g_f.scale_vector(norm_col, 255)
        self._rgb_font = color, self._rgb_font[1]

    def set_size(self, font_size):
        """changes font size"""

        self._hsv_font = self._hsv_font[0], int(max(min(30, font_size), 0))
        self._rgb_font = self._rgb_font[0], int(max(min(30, font_size), 0))

    def hsv_font(self):
        """getter"""

        return self._hsv_font

    def point_list(self):
        """getter"""

        return self._point_list

    def set_point_list(self, point_list):
        """setter"""

        self._point_list = point_list
        self.full_redraw()

    def enable_clearing(self, value):
        """enables or disable clearing"""

        self._layer.layer_objects["click clear"].disabled = not value

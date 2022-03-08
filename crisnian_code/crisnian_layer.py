from pygui import colors as col, layer
from crisnian_code import animation, manual, file_manager
from crisnian_code import layer_utilities as l_u
from utility_functions import geometrical_functions as g_f
import pygame
import colorsys
import os


WHITE = col.WHITE
LIGHT_GREY = col.LIGHT_GREY
DEMI_GREY = col.DEMI_GREY
GREY = col.GREY
BLUE = col.BLUE
RED = col.RED
BLACK = col.BLACK

MANUAL_DRAWING_ALPHA = 50
DEFAULT_FRAME_RATE = 5


class CrisnianLayer(layer.Layer):
    """Contains a manual drawing object, an animation object,
    a file manager, and user interface elements."""

    def __init__(self, g_u_i, size):
        """initialize manual drawing object, animation object,
        file manager, and user interface elements"""

        super().__init__(g_u_i, size)
        pygame.mouse.set_visible(False)
        
        # manual drawing
        self.manual = manual.Manual(self, self.size, MANUAL_DRAWING_ALPHA)
        self.font_selection = 0
        
        # clock drawing animation
        self.animation = animation.Animation(self, DEFAULT_FRAME_RATE,
                                             self.manual, self.size)
        self.manual.animation(self.animation)

        # file manager for import/export
        self.file_manager = file_manager.FileManager(self, self.manual,
                                                     self.animation)

        # control of input
        self.start_manual_drawing = False
        self.first_manual_point = False
        self.cur_pos = 0, 0

        # interface icons
        load = pygame.image.load
        self.draw_cursor_icon_icon = load(os.path.join("icons", "draw.png"))
        self.erase_cursor_icon = load(os.path.join("icons", "erase.png"))
        self.click_cursor_icon = load(os.path.join("icons", "click.png"))
        self.hue_area = load(os.path.join("icons", "hue.png"))
        self.size_area = load(os.path.join("icons", "size.png"))

        # dictionary of all user interface elements
        an = self.animation
        m = self.manual
        f_m = self.file_manager
        layer_objects = {
            "animation": ("label", 20, 30, "Animation", True),
            "speed": ("click", 135, 30, 1.3, "", an.speed, "speed", False),
            "time": ("label", 160, 30, "0:00", True),
            "render": ("click", 30, 70, 1.3, "Render", an.render, "render", True),
            "render%": ("label", 130, 70, "0%", True),
            "play/pause": ("toggle", 30, 110, 1.3, "Play/Pause", an.play,
                           "play", "pause", True, True),
            "play%": ("label", 170, 110, "0%", True),
            "restart": ("click", 30, 150, 1.3, "Restart", an.restart, "reset", True),
            "drawing": ("label", 20, 200, "Drawing", True, False),
            "show/hide": ("toggle", 30, 240, 1.3, "Show/Hide", m.show,
                          "hide", "show", False),
            "clear": ("click", 30, 280, 1.3, "Clear", m.clear, "clear", False),
            "draw/erase": ("toggle", 30, 320, 1.3, "Draw/Erase", m.erase,
                           "erase", "draw", False),
            "file": ("label", 30, 540, "File", True),
            "import": ("click", 30, 580, 1.3, "Import", f_m.importing, "import", False),
            "export": ("click", 30, 620, 1.3, "Export", f_m.exporting, "export", True),
            "export%": ("label", 130, 620, "0%", True),
        }

        # fill the layer object list with user interface elements
        for name, o_i in layer_objects.items():

            # get head properties
            obj_type = o_i[0]
            full_name = obj_type + " " + name
            pos = o_i[1], o_i[2]

            # check if an object type was found
            matched = False

            # click buttons
            if obj_type == "click":
                matched = True

                # load icon if found
                image = o_i[6]
                if image is not None:
                    image = "icons/" + o_i[6] + ".png"

                # generate object
                obj = layer.Button(self, LIGHT_GREY, pos, 10 * o_i[3],
                                   o_i[4], (o_i[5], ()), bold=True,
                                   inv=True, image=image, disabled=o_i[7])
            # toggle buttons
            elif obj_type == "toggle":
                matched = True

                # load icon if found
                image1 = o_i[6]
                if image1 is not None:
                    image1 = "icons/" + o_i[6] + ".png"
                image2 = o_i[7]
                if image2 is not None:
                    image2 = "icons/" + o_i[7] + ".png"

                # generate object
                obj = layer.ToggleButton(self, LIGHT_GREY, pos, 10 * o_i[3],
                                         o_i[4], (o_i[5], ()), bold=True,
                                         inv=True, image1=image1, image2=image2,
                                         disabled=o_i[8])
            # label object
            elif obj_type == "label":
                matched = True
                obj = layer.Label(self, o_i[3], LIGHT_GREY, pos, bold=o_i[4])

            # None found
            else:
                obj = None

            # add layer object to list
            if matched:
                self.layer_objects[full_name] = obj

    def redraw(self):
        """draws interface elements and manual/animation layers"""

        # menu offset
        off = self.size[0] - self.size[1]

        # draw the drawing board background
        self.surface.fill(WHITE)

        # draw the manual drawing
        if self.manual.is_showing():
            self.surface.blit(self.manual.drawing(), (off, 0))

        # draw animation frame and advance the animation
        if self.animation.is_rendered() and not self.animation.is_rendering():
            if self.animation.non_empty():
                self.surface.blit(self.animation.frame(), (off, 0))
            if self.animation.is_playing():
                self.animation.next()

        # draw the menu background
        pygame.draw.rect(self.surface, GREY, (0, 0, off, self.size[1]), 0)

        # draw hue selectors
        hsv = self.manual.hsv_font()[0]
        self.surface.blit(self.hue_area, (30, 350))
        x = 30 + hsv[0]*(150/1)
        pygame.draw.line(self.surface, BLACK, (x, 350), (x, 380), 2)

        # draw saturation selector
        left_color = g_f.scale_vector(colorsys.hsv_to_rgb(hsv[0], 0, hsv[2]), 255)
        right_color = g_f.scale_vector(colorsys.hsv_to_rgb(hsv[0], 1, hsv[2]), 255)
        self.gradientRect(left_color, right_color, ((30, 390), (180, 420)))
        x = 30 + hsv[1] * (150 / 1)
        pygame.draw.line(self.surface, BLACK, (x, 390), (x, 420), 2)

        # draw value selector
        left_color = g_f.scale_vector(colorsys.hsv_to_rgb(hsv[0], hsv[1], 0), 255)
        right_color = g_f.scale_vector(colorsys.hsv_to_rgb(hsv[0], hsv[1], 1), 255)
        self.gradientRect(left_color, right_color, ((30, 430), (180, 460)))
        x = 30 + hsv[2] * (150 / 1)
        pygame.draw.line(self.surface, BLACK, (x, 430), (x, 460), 2)

        # draw font size selectors
        self.surface.blit(self.size_area, (30, 470))
        x = 30 + self.manual.hsv_font()[1]*(150/30)
        pygame.draw.line(self.surface, BLACK, (x, 470), (x, 500), 2)

    def post_redraw(self):
        """draws cursor and grey drawing lock"""

        # draw cursor
        if self.cur_pos[0] > self.size[0] - self.size[1]:
            font_size = self.manual.hsv_font()[1]
            pygame.draw.circle(self.surface, BLACK, self.cur_pos, font_size/2, 1)
            if self.manual.is_erasing():
                self.surface.blit(self.erase_cursor_icon, self.cur_pos)
            else:
                self.surface.blit(self.draw_cursor_icon_icon, self.cur_pos)
        else:
            self.surface.blit(self.click_cursor_icon, self.cur_pos)

        # draw grey drawing lock
        if self.animation.is_rendering() \
                or not self.manual.is_showing() \
                or self.file_manager.is_exporting():
            surf = pygame.Surface((self.size[1], self.size[1]), pygame.SRCALPHA)
            surf.set_alpha(100)
            surf.fill(BLACK)
            self.surface.blit(surf, (self.size[0]-self.size[1], 0))

    def tick(self, cur_pos):
        """captures the mouse drawing/erasing
        and change of font"""

        # record cursor position and get its complex version
        self.cur_pos = cur_pos
        cur_comp = l_u.board_to_complex(self.size, cur_pos)

        # asks for screen refresh
        self.g_u_i.to_draw_all()

        # change font
        if self.font_selection == 1:
            self.manual.set_hue((cur_pos[0]-30)*(1/150))
        elif self.font_selection == 2:
            self.manual.set_sat((cur_pos[0]-30)*(1/150))
        elif self.font_selection == 3:
            self.manual.set_val((cur_pos[0]-30)*(1/150))
        elif self.font_selection == 4:
            self.manual.set_size((cur_pos[0]-30)*(30/150))

        # only do things when drawing
        if not self.start_manual_drawing:
            return

        # draw if drawing
        if not self.manual.is_erasing():

            # do not connect first manual point to previous one
            if self.first_manual_point:
                self.manual.increment(cur_comp)
                self.first_manual_point = False
            # for non-first manual points, add multiple intermediate
            # points to ensure connection
            else:
                old_z = self.manual[-1]
                d = int(l_u.c_mod(cur_comp - old_z[0]))
                for inter in range(d):
                    self.manual.increment((cur_comp-old_z[0])*((inter+1)/d)+old_z[0])

        # erase points if erasing
        else:
            # only keep points that are outside the cursor range
            new_point_list = []
            for point, font in self.manual.point_list():
                if l_u.c_mod(point - cur_comp) > self.manual.hsv_font()[1]/2:
                    new_point_list.append((point, font))

            self.manual.set_point_list(new_point_list)

        self.animation.update_time()

    def mouse_button_up(self, event, cur_pos):
        """checks if mouse is not pressed anymore"""

        # reset font selection
        self.font_selection = 0

        # stop manual drawing
        if self.start_manual_drawing:
            self.animation.no_render()
            self.start_manual_drawing = False

    def mouse_button_down(self, event, cur_pos):
        """checks if mouse is pressed inside drawing area,
        or on font selection interface"""

        # cannot draw if rendering or if drawing is hidden
        if self.animation.is_rendering()\
                or not self.manual.is_showing()\
                or self.file_manager.is_exporting():
            return

        # checks if the user is drawing
        if cur_pos[0] > (self.size[0] - self.size[1]):
            self.start_manual_drawing = True
            self.first_manual_point = True
            self.animation.no_render()

        # checks if the user is selecting a font
        elif 30 < cur_pos[0] < 180 and 350 < cur_pos[1] < 380:
            self.font_selection = 1
        elif 30 < cur_pos[0] < 180 and 390 < cur_pos[1] < 420:
            self.font_selection = 2
        elif 30 < cur_pos[0] < 180 and 430 < cur_pos[1] < 460:
            self.font_selection = 3
        elif 30 < cur_pos[0] < 180 and 470 < cur_pos[1] < 500:
            self.font_selection = 4

    def gradientRect(self, left_colour, right_colour, target_rect):
        """ Draw a horizontal-gradient filled rectangle
        covering <target_rect> """

        colour_rect = pygame.Surface((2, 2))
        pygame.draw.line(colour_rect, left_colour, (0, 0), (0, 1))
        pygame.draw.line(colour_rect, right_colour, (1, 0), (1, 1))
        size = g_f.sub_vectors(target_rect[1], target_rect[0])
        colour_rect = pygame.transform.smoothscale(colour_rect, size)
        self.surface.blit(colour_rect, target_rect[0])

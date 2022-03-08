import pygame
import os
import json


class GUI:
    """pygame GUI object that stores multiple layers,
    with functions to change font/icon, load/save settings,
    request layer drawing, and quit. Intended to wok with
    gui_input_manager_loop function"""

    def __init__(self, name, size, fps):

        # dashboard initialization
        pygame.init()
        pygame.display.set_caption(name)
        self.size = size
        self.screen = pygame.display.set_mode(self.size)

        # frames per second and regular updates per second
        self.fps = fps

        # window crisnian_code
        self.layers = {}
        self.layers_order = []

        # default font type and size
        self.font_size = None
        self.font_type = None
        self.font = None
        self.font_u = None
        self.font_b = False

        # stored settings
        self.settings = {}
        self.settings_file_name = None

        # quit request
        self.quit_request = False

    def quit(self):
        """requests a full quit of all threads"""

        self.quit_request = True

    def load_settings(self, settings_file_name, default_settings):

        # load or create display settings
        self.settings_file_name = settings_file_name
        if os.path.exists(settings_file_name):
            with open(settings_file_name, "r") as file:
                self.settings = json.load(file)
        else:
            with open(settings_file_name, "w") as file:
                json.dump(default_settings, file)
                self.settings = default_settings

    def set_font(self, font_type, font_size):
        """sets the font type and size"""

        # font for drawing
        pygame.font.init()
        self.font_size = font_size
        self.font_type = font_type
        SF = pygame.font.SysFont
        self.font = SF(self.font_type, self.font_size)
        self.font_u = SF(self.font_type, self.font_size)
        self.font_u.set_underline(True)
        self.font_b = SF(self.font_type, self.font_size)
        self.font_b.set_bold(True)

    def add_layer(self, layer_name, layer):
        """add gui layer to the window"""

        self.layers[layer_name] = layer
        self.layers_order.append(layer_name)

    def to_draw(self, layer_name):
        """requests a layer to be redrawn"""

        self.layers[layer_name].to_draw = True

    def to_draw_all(self):
        """request all crisnian_code to be redrawn"""

        for key in self.layers:
            self.to_draw(key)

    def save_settings(self):
        """closes the gui and saves settings"""

        file_name = self.settings_file_name
        if file_name is not None:
            with open(self.settings_file_name, "w") as file:
                json.dump(self.settings, file)
        pygame.quit()

    @staticmethod
    def set_icon(image_path):
        """sets the icon of the GUI"""

        pygame.display.set_icon(pygame.image.load(image_path))

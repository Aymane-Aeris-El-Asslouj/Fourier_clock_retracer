from utility_functions import geometrical_functions as g_f
from pygui import colors as col

import pygame


def emp():
    """empty function"""
    
    pass


GREY = (100, 100, 100)
EMP = (emp, ())
WHITE = col.WHITE
RED = col.RED


def call(func_with_args):
    """call function with arguments"""

    func_with_args[0](*func_with_args[1])


class Layer:
    """parent class for GUI crisnian_code, contains
    a surface that can be redrawn"""

    def __init__(self, g_u_i, size):

        """defines if the layer only takes up
        half the window"""
        self.size = size

        # initialize the layer's surface
        self.surface = None
        self.reset()

        # store reference to GUI window
        self.g_u_i = g_u_i
        self.font = g_u_i.font
        self.font_u = g_u_i.font_u
        self.font_b = g_u_i.font_b

        # stores whether the surface needs to be redrawn
        self.to_draw = False

        """list of objects stored inside the layer"""
        self.layer_objects = {}

    def reset(self):
        """resets the layer's surface"""

        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)

    def update(self):
        """update the current layer resetting
        it and redrawing it"""

        # reset surface
        self.reset()

        # redraw surface
        self.redraw()

        # redraw objects of layer and add blit their surface
        for object_key in self.layer_objects:
            layer_obj = self.layer_objects[object_key]
            layer_obj.redraw()

        # post redraw surface
        self.post_redraw()

    def redraw(self):
        """redraws the layer's surface"""

        pass

    def post_redraw(self):
        """post redraws the layer's surface"""

        pass

    def tick_event(self, cur_pos):
        """react to window regular tick"""

        self.tick(cur_pos)

        # transfer tick event to objects
        for object_key in self.layer_objects:
            self.layer_objects[object_key].tick_event(cur_pos)

    def tick(self, cur_pos):
        """react to tick event"""

        pass

    def event(self, cur_pos, event):
        """reacts to a certain window event"""

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_button_down(event, cur_pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_button_up(event, cur_pos)

        elif event.type == pygame.KEYDOWN:
            self.key_down(event, cur_pos)

        # transfer events to objects
        for object_key in self.layer_objects:
            self.layer_objects[object_key].event(event)

    def mouse_button_down(self, event, cur_pos):
        """reacts to mouse button down event"""

        pass

    def mouse_button_up(self, event, cur_pos):
        """reacts to mouse button up event"""

        pass

    def key_down(self, event, cur_pos):
        """reacts to key down event"""

        pass


class LayerObject:
    """parent class for layer objects,
    draws on a layer surface"""

    def __init__(self, layer):

        # store reference to GUI window
        self.layer = layer
        self.font = layer.font
        self.font_b = layer.font_b

    def redraw(self):
        """redraws the layer's surface"""

        pass

    def tick_event(self, cur_pos):
        """react to window regular tick"""

        pass

    def event(self, event):
        """reacts to a certain window event"""

        # get cursor position on screen and on map
        cur_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_button_down(event, cur_pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_button_up(event, cur_pos)

        elif event.type == pygame.KEYDOWN:
            self.key_down(event, cur_pos)

    def mouse_button_down(self, event, cur_pos):
        """reacts to mouse button down event"""

        pass

    def mouse_button_up(self, event, cur_pos):
        """reacts to mouse button up event"""

        pass

    def key_down(self, event, cur_pos):
        """reacts to key down event"""

        pass


class Label(LayerObject):
    """label draws text on layer"""

    def __init__(self, layer, text, color, pos, bold=False):
        super().__init__(layer)
        self.text = text
        self.color = color
        self.pos = pos
        self.bold = bold

    def redraw(self):
        """draw text on layer"""

        if self.bold:
            label = self.font_b.render(self.text, True, self.color)
        else:
            label = self.font.render(self.text, True, self.color)
        label_pos = label.get_rect(midleft=self.pos)
        self.layer.surface.blit(label, label_pos)


class Button(LayerObject):
    """General button class, implements three-button clicking,
    along with button icon, button label, highlight upon hovering,
    and disabled status"""

    def __init__(self, layer, color, pos, size, text,
                 left=EMP, middle=EMP, right=EMP, bold=False,
                 inv=False, image=None, disabled=False):
        super().__init__(layer)

        # button parameters
        self.color = color
        self.pos = pos
        self.size = size
        self.text = text
        self.bold = bold
        self.inv = inv
        self.disabled = disabled

        # loads image if it is not None
        if image is not None:
            self.image = pygame.image.load(image)
        else:
            self.image = None

        # change color when hovering
        self.hover = False

        # for shining after click
        self.clicked = False

        # click actions
        self.left_action = lambda: call(left)
        self.middle_action = lambda: call(middle)
        self.right_action = lambda: call(right)

    def mouse_button_up(self, event, cur_pos):
        """react to mouse button down event"""

        self.clicked = False

    def mouse_button_down(self, event, cur_pos):
        """react to mouse button down event"""

        # check if cursor is inside button
        if self.collision_check(cur_pos):

            # left click
            if event.button == 1:
                self.left_action()
                self.clicked = True

            # middle click
            if event.button == 2:
                self.middle_action()
                self.clicked = True

            # right click
            if event.button == 3:
                self.right_action()
                self.clicked = True

    def highlight(self):
        """highlights the button when hovered or clicked"""

        # only highlight if button is enabled
        if not self.disabled:

            surf = pygame.Surface(self.layer.size, pygame.SRCALPHA)
            
            # highlight at different levels
            # when clicked and when hovered
            if self.clicked:
                surf.set_alpha(60)
            elif self.hover:
                surf.set_alpha(30)
            else:
                surf.set_alpha(0)

            # make the highlight a little larger than the actual button
            size_new = self.size*3
            hover_rect = (self.pos[0] - size_new/2,
                          self.pos[1] - size_new/2, size_new, size_new)
            pygame.draw.rect(surf, WHITE, hover_rect, 0, 2)
            self.layer.surface.blit(surf, (0, 0))

    def redraw(self):
        """draw circle on layer"""

        # draw highlight before if inv is False
        if not self.inv:
            self.highlight()

        # draw button and its label
        self.draw_button_label(self.layer.surface, self.color)

        # draw highlight on top if inv is true
        if self.inv:
            self.highlight()

    def draw_button_label(self, surface, color):
        """draw button and its label"""

        # draw button circle if button has no image
        if self.image is None:
            pygame.draw.circle(surface, color,
                               self.pos, self.size)
        # draw image and label if button has image
        else:
            # draw greyed image if button is disabled
            if self.disabled:
                surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                surf.set_alpha(50)
                surf.blit(self.image, g_f.linear_vectors(1, self.pos, -1/2,
                                                         self.image.get_size()))
                surface.blit(surf, (0, 0))
            else:
                surface.blit(self.image, g_f.linear_vectors(1, self.pos, -1/2,
                                                            self.image.get_size()))
        # draw text on layer
        if self.bold:
            label = self.font_b.render(self.text, True,
                                       color)
        else:
            label = self.font.render(self.text, True,
                                     color)

        # draw label to the right of the button
        pos = g_f.add_vectors(self.pos, (self.size * 2, 0))
        label_pos = label.get_rect(midleft=pos)

        # draw a greyed out version of the label if the
        # button is disabled
        if self.disabled:
            surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            surf.set_alpha(50)
            surf.blit(label, label_pos)
            surface.blit(surf, (0, 0))

        else:
            surface.blit(label, label_pos)

    def tick_event(self, cur_pos):
        """react to window tick event"""

        # change hover status when cursor inside
        # or outside button
        if self.collision_check(cur_pos):
            if not self.hover:
                self.hover = True
        else:
            if self.hover:
                self.hover = False
        self.layer.to_draw = True

    def collision_check(self, cur_pos):
        """checks if cursor collides with button"""

        return g_f.distance_2d(cur_pos, self.pos) < self.size


class InputButton(Button):
    """button with radio size toggle function, middle deactivation,
    and right action with arguments"""

    def __init__(self, layer, color, pos, size, text,
                 left=EMP, middle=EMP, right=EMP):

        """list of other buttons in the same radio group,
        such that only one can be on at the same time"""
        self.radio = []

        self.on = False
        self.activated = True

        # if active, switch its on state
        def l_action():
            if self.activated:
                if self.on:
                    self.turn_off()
                else:
                    self.turn_on()
                self.layer.to_draw = True
            call(left)

        # switch activation state
        def m_action():
            if self.activated:
                self.deactivate()
            else:
                self.activate()
            self.layer.to_draw = True
            call(middle)

        # call button constructor
        super().__init__(layer, color, pos, size, text,
                         (l_action, ()), (m_action, ()), right)

    def turn_on(self):
        """switch mode to on and others' to off"""

        if not self.on:
            self.on = True
            self.size *= 5/4

            for button in self.radio:
                if button is not self:
                    button.turn_off()

    def turn_off(self):
        """switch mode to off"""

        if self.on:
            self.on = False
            self.size *= 4/5

    def activate(self):
        """activates button"""

        if not self.activated:
            self.activated = True

    def deactivate(self):
        """activates button"""

        if self.activated:
            self.activated = False
            self.turn_off()

    def redraw(self):
        """draw self with text in color if active
        or grey otherwise"""

        # draw hover and clicked circles
        self.highlight()

        # draw button and create label for text
        if self.activated:
            color = self.color
        else:
            color = GREY
        pygame.draw.circle(self.layer.surface, color,
                           self.pos, self.size)
        label = self.font.render(self.text, True, color)

        # draw text on layer
        pos = g_f.add_vectors(self.pos, (self.size * 2, 0))
        label_pos = label.get_rect(midleft=pos)
        self.layer.surface.blit(label, label_pos)


class ToggleButton(Button):
    """General toggle button class derived from Button,
    implements on-off status"""

    def __init__(self, layer, color, pos, size, text,
                 left=EMP, middle=EMP, right=EMP, bold=True,
                 inv=True, image1=None, image2=None, disabled=False):

        self.on = True

        # load images if not None
        if image1 is not None:
            self.image1 = pygame.image.load(image1)
        else:
            self.image1 = None
        if image2 is not None:
            self.image2 = pygame.image.load(image2)
        else:
            self.image2 = None

        # if active, switch its on state
        def l_action():
            if self.on:
                self.turn_off()
            else:
                self.turn_on()
            self.layer.to_draw = True
            call(left)

        # call button constructor
        super().__init__(layer, color, pos, size, text,
                         (l_action, ()), middle, right,
                         bold, inv, disabled=disabled)

    def draw_button_label(self, surface, color):

        # draw button circle if no image is available
        if self.image1 is None:
            pygame.draw.circle(surface, color,
                               self.pos, self.size)
        else:

            # pick the on or off image
            if self.on:
                img = self.image1
            else:
                img = self.image2

            # draw a greyed out version of the image if the
            # button is disabled
            if self.disabled:
                surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                surf.set_alpha(50)
                surf.blit(img, g_f.linear_vectors(1, self.pos, -1/2,
                                                  self.image1.get_size()))
                surface.blit(surf, (0, 0))
            else:
                surface.blit(img, g_f.linear_vectors(1, self.pos, -1/2,
                                                     self.image1.get_size()))

        if self.bold:
            label = self.font_b.render(self.text, True,
                                       color)
        else:
            label = self.font.render(self.text, True,
                                     color)

        # draw the label to the right of the button
        pos = g_f.add_vectors(self.pos, (self.size * 2, 0))
        label_pos = label.get_rect(midleft=pos)

        # draw a greyed out version of the label if the
        # button is disabled
        if self.disabled:
            surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            surf.set_alpha(50)
            surf.blit(label, label_pos)
            surface.blit(surf, (0, 0))

        else:
            surface.blit(label, label_pos)

    def turn_on(self):
        """switch mode to on and others' to off"""

        if not self.on:
            self.on = True

    def turn_off(self):
        """switch mode to off"""

        if self.on:
            self.on = False


class SettingInputButton(InputButton):
    """input button that saves state to settings"""

    def __init__(self, layer, color, pos, size, text, setting,
                 left=EMP, middle=EMP, right=EMP):
        super().__init__(layer, color, pos, size,
                         text, left, middle, right)

        # store setting name
        self.setting = setting

        # create or load setting
        settings = self.layer.g_u_i.settings
        if self.setting not in settings:
            settings[self.setting] = {
                "on": False,
                "activated": True
            }
        if settings[self.setting]["on"]:
            self.turn_on()
        if not settings[self.setting]["activated"]:
            self.deactivate()

    def turn_on(self):
        """switch mode to on and others' to off"""

        if not self.on:
            self.on = True
            self.size *= 5/4

            for button in self.radio:
                if button is not self:
                    button.turn_off()

        self.layer.g_u_i.settings[self.setting]["on"] = self.on

    def turn_off(self):
        """switch mode to off"""

        if self.on:
            self.on = False
            self.size *= 4/5

        self.layer.g_u_i.settings[self.setting]["on"] = self.on

    def activate(self):
        """activates button"""

        if not self.activated:
            self.activated = True

        self.layer.g_u_i.settings[self.setting]["activated"] = self.activated

    def deactivate(self):
        """activates button"""

        if self.activated:
            self.activated = False
            self.turn_off()

        self.layer.g_u_i.settings[self.setting]["activated"] = self.activated


class SettingToggleButton(ToggleButton):
    """toggle button that saves state to settings"""

    def __init__(self, layer, color, pos, size, text, setting,
                 left=EMP, middle=EMP, right=EMP):
        super().__init__(layer, color, pos, size,
                         text, left, middle, right)

        # store setting name
        self.setting = setting

        # load or create setting
        settings = self.layer.g_u_i.settings
        if self.setting not in settings:
            settings[self.setting] = {
                "on": True,
            }
        if not settings[self.setting]["on"]:
            self.turn_off()

    def turn_on(self):
        """switch mode to on and others' to off"""

        if not self.on:
            self.on = True

        self.layer.g_u_i.settings[self.setting]["on"] = self.on

    def turn_off(self):
        """switch mode to off"""

        if self.on:
            self.on = False

        self.layer.g_u_i.settings[self.setting]["on"] = self.on


class DragAndDrop(Button):
    """Object that can be dragged around"""

    def __init__(self, layer, color, pos, size, text):

        # store position
        super().__init__(layer, color, pos, size, text)

        # variables for dragging
        self.initial_cur_pos = None
        self.initial_pos = None
        self.dragged = False

    def mouse_button_down(self, event, cur_pos):
        """reacts to mouse button down event"""

        super().mouse_button_down(event, cur_pos)

        # start dragging if clicked on
        if event.button == 1:
            if g_f.distance_2d(cur_pos, self.pos) < self.size:
                self.dragged = True
                self.initial_cur_pos = cur_pos
                self.initial_pos = self.pos

    def mouse_button_up(self, event, cur_pos):
        """react to mouse button up event"""

        super().mouse_button_up(event, cur_pos)

        # stop dragging if click released
        if event.button == 1:
            self.dragged = False

    def tick_event(self, cur_pos):
        """react to tick event"""

        super().tick_event(cur_pos)

        # update position and clicked during drag
        if self.dragged:
            self.clicked = 5
            cur_diff = g_f.sub_vectors(cur_pos, self.initial_cur_pos)
            self.pos = g_f.add_vectors(self.initial_pos, cur_diff)

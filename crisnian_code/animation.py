import threading
import cmath
from pygui import colors as col, drawing_functions as d_f
import pygame
from utility_functions import geometrical_functions as g_f
from crisnian_code import layer_utilities as l_u
import tkinter as tk
from tkinter import simpledialog

BLACK = col.BLACK
GREEN = col.GREEN
RED = col.RED


class Animation:
    """generates and stores screen animation
    using Fourier analysis function"""

    def __init__(self, layer, animation_speed, manual, size):

        self._frames = []  # animation frames
        self._frame = 0
        self._animation_speed = animation_speed
        self._fonts = []
        self._playing = False
        self._manual = manual
        self._size = size[1], size[1]
        self._rendered = False
        self._rendering = False
        self._layer = layer
        self._asking = False

    def non_empty(self):
        """checks if the animation is not empty"""

        return len(self._frames) > 0

    def frame(self):
        """returns current frame"""

        return self._frames[self._frame]

    def next(self):
        """advances the animation"""

        # advance the frame based on animation speed
        self._frame = min(self._frame + 1, len(self._frames) - 1)

        # update animation percentage
        self.display_animation_percentage()

        # pause if the last frame is reached
        if self._frame == len(self._frames) - 1:
            self.pause()
            self._layer.layer_objects["label play%"].text = "100%"

    def clear(self):
        """clears all frames"""

        self._frames.clear()

    def restart(self):
        """restarts animation"""

        self.pause()
        self._frame = 0

        # update animation percentage
        self.display_animation_percentage()

    def add_frame(self, frame):
        """adds new frame"""

        self._frames.append(frame)
        
    def render(self):
        """renders the animation"""

        # cannot render if rendering or already rendered
        # or if not enough points or if asking for frame rate change
        # or if currently importing drawing
        if self.is_rendering() or self.is_rendered()\
            or len(self._manual.point_list()) < 2\
                or self._asking or self._layer.file_manager.is_importing():
            return

        # disable actions that compromise rendering
        self._manual.enable_clearing(False)
        self._layer.file_manager.enable_importing(False)
        self.enable_rendering(False)
        self.enable_speed(False)

        # start rendering the clock animation
        self._rendering = True

        # get list of manual points and save their font
        points_only = [point for point, font in self._manual.point_list()]
        self._fonts = [font for point, font in self._manual.point_list()]

        # start rendering
        threading.Thread(target=self._render_animation,
                         args=(points_only,)).start()

    def play(self):
        """either starts playing the animation or pauses it"""

        # flip the state of animation playing
        # cannot play while rendering or if no render
        if not self._playing and self._rendered and not self.is_rendering():

            # reset animation if it reached the end
            if self._frame == len(self._frames) - 1:
                self._frame = 0

                # update animation percentage
                self.display_animation_percentage()

            self._playing = True
            self._layer.layer_objects["toggle play/pause"].turn_off()
        else:
            self.pause()

    def pause(self):
        """pauses animation"""

        self._playing = False
        self._layer.layer_objects["toggle play/pause"].turn_on()

    def no_render(self):
        """marks animation as not rendered because it was updated"""

        # reset animation and related actions
        self.pause()
        self.clear()
        self._rendered = False
        self._frame = 0
        self.display_rendering_percentage(0)
        self.display_animation_percentage()
        self._layer.layer_objects["label export%"].text = "0%"

        # disable actions that require a render
        self._layer.file_manager.enable_exporting(False)
        self.enable_playing(False)
        self.enable_restarting(False)

        # enable rendering if there are enough points
        self.enable_rendering(False)
        if len(self._manual.point_list()) > 1:
            self.enable_rendering(True)

    def display_rendering_percentage(self, percent):
        """displays percentage of rendering on screen"""

        self._layer.layer_objects["label render%"].text = str(percent) + "%"

    def display_animation_percentage(self):
        """displays animation percentage"""

        if self.non_empty():
            percent = int(100 * self._frame / len(self._frames))
        else:
            percent = 0
        self._layer.layer_objects["label play%"].text = str(percent) + "%"

    def _render_animation(self, points_only):
        """Creates the clock drawing animation.
        Get clock coefficient with fourier analysis,
        then draw stack clocks to draw"""

        # ratio for how much computation time fourier analysis takes
        # relatively to screen drawing (measured empirically)
        ratio = 126/(self._animation_speed+2.1)

        # percentage of computation time fourier analysis takes
        # relatively to screen drawing (measured empirically)
        percent_split = 100/(ratio+1)

        # compute clock coefficients using fourier analysis
        clock_sizes = []
        fourier = l_u.discrete_fourier_transform
        fourier(points_only, clock_sizes,
                self._layer.g_u_i, self, percent_split)

        # stop rendering if requested
        if self._layer.g_u_i.quit_request:
            return

        # clear any previous animation
        self.clear()

        # number of clocks
        N = len(clock_sizes)

        # board that records the clock drawing
        drawing_board = pygame.Surface(self._size, pygame.SRCALPHA)

        # go through every drawing point
        for k in range(N):

            # stop rendering if requested
            if self._layer.g_u_i.quit_request:
                return

            # get color and size from font
            color = self._fonts[k][0]
            size = self._fonts[k][1]

            # show new completion percentage
            if k % self._animation_speed == 0:
                percent = int(percent_split + (100-percent_split) * (k / N))
                self.display_rendering_percentage(percent)

            # create new drawing frame
            if k % self._animation_speed == 0:
                frame_k = pygame.Surface(self._size, pygame.SRCALPHA)
                frame_k.blit(drawing_board, (0, 0))
            else:
                frame_k = None

            # draw clocks
            new_center = 0
            exp_base = cmath.exp(-2j * cmath.pi * k / N)
            new_exp = exp_base ** (int(N / 2))
            c_s = clock_sizes
            for n, cof in enumerate(c_s[int(N / 2):] + c_s[:int(N / 2)]):

                # get size of clocks
                cof_mod = l_u.c_mod(cof)

                # get new clock term
                exp = cof * new_exp

                proj_new_center = l_u.complex_to_board(self._size, new_center)
                next_proj_center = l_u.complex_to_board(self._size,
                                                        new_center + exp)

                # only draw clocks if the frame will show up in the animation
                if k % self._animation_speed == 0:

                    pygame.draw.circle(frame_k, BLACK, proj_new_center,
                                       cof_mod, 2)
                    # draw arrow to point and point in green
                    if cof != 0:
                        d_f.draw_arrow(frame_k, proj_new_center,
                                       (exp.real, -exp.imag),
                                       BLACK, cof_mod / 100)
                    pygame.draw.circle(frame_k, GREEN, next_proj_center, 2, 0)

                # update drawing reference
                new_center += exp
                new_exp *= exp_base

            # add an new line to the clock drawing if there was no jump
            if k != 0 and g_f.distance_2d(next_proj_center, proj_old_center) < 2:
                pygame.draw.line(drawing_board, color,
                                 next_proj_center, proj_old_center, size)

            proj_old_center = next_proj_center

            # print clock drawing tip in red
            if k % self._animation_speed == 0:
                pygame.draw.circle(frame_k, RED, next_proj_center, 2, 0)

            # add new frame to animation
            if k % self._animation_speed == 0:
                self.add_frame(frame_k)

        # add a frame with only the final drawing
        self.add_frame(drawing_board)

        self.display_rendering_percentage(100)

        # mark the animation as rendered and enable actions
        # that compromise or require rendering
        self._rendering = False
        self._layer.file_manager.enable_exporting(True)
        self._manual.enable_clearing(True)
        self.enable_playing(True)
        self.enable_restarting(True)
        self._layer.file_manager.enable_importing(True)
        self.enable_speed(True)
        self._rendered = True

    def is_rendering(self):
        """getter"""

        return self._rendering

    def is_rendered(self):
        """getter"""

        return self._rendered

    def is_playing(self):
        """getter"""

        return self._playing

    def speed(self):
        """launches spe"""

        if not self._asking:

            self._asking = True
            self.enable_rendering(False)
            self._layer.file_manager.enable_exporting(False)
            threading.Thread(target=self.spe).start()

    def spe(self):
        """asks the user for the animation speed"""

        # cannot change speed while rendering or exporting or importing
        if self._rendering or self._layer.file_manager.is_exporting():
            return

        self.pause()

        # ask user of frame speed
        root = tk.Tk()
        root.withdraw()
        answer = simpledialog.askinteger("Input", "Frame speed?", minvalue=1,
                                         initialvalue=self._animation_speed)
        root.destroy()

        if answer is not None:
            self._animation_speed = answer

        self.no_render()
        self.update_time()
        self._asking = False

    def asking(self):
        """getter"""

        return self._asking

    def frames(self):
        """getter"""

        return self._frames

    def animation_speed(self):
        """getter"""

        return self._animation_speed

    def update_time(self):
        """updates animation time"""

        # how long a video is based on number of frames
        time = len(self._manual.point_list())/(20*self._animation_speed)

        # generate time string from seconds
        if int(time % 60) < 10:
            time = str(int(time/60)) + ":0" + str(int(time % 60))
        else:
            time = str(int(time/60)) + ":" + str(int(time % 60))

        self._layer.layer_objects["label time"].text = time

    def enable_rendering(self, value):
        """enables or disable rendering"""

        self._layer.layer_objects["click render"].disabled = not value

    def enable_playing(self, value):
        """enables or disable playing"""

        self._layer.layer_objects["toggle play/pause"].disabled = not value

    def enable_restarting(self, value):
        """enables or disable restarting"""

        self._layer.layer_objects["click restart"].disabled = not value

    def enable_speed(self, value):
        """enables or disable speed change"""

        self._layer.layer_objects["click speed"].disabled = not value

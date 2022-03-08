import pygame
from pygui import colors as col
import os
import cv2
import threading
from scipy.integrate import quad

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import svgelements

WHITE = col.WHITE


class FileManager:

    def __init__(self, layer, manual, animation):
        self._layer = layer
        self._manual = manual
        self._animation = animation
        self._exporting = False
        self._importing = False

    def importing(self):
        """launch importing"""

        if not self._importing and not self._exporting\
                and not self._layer.animation.asking()\
                and not self._animation.is_rendering():

            self._importing = True
            self.enable_exporting(False)
            self._animation.enable_rendering(False)
            threading.Thread(target=self.imp).start()

    def imp(self):
        """Import svg file"""

        # Create temp directory if it does not exist
        if not os.path.exists("samples"):
            os.makedirs("samples")

        # get file output
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            defaultextension='.svg', filetypes=[("svg", '*.svg')],
            initialdir="samples", title="Choose svg")
        root.destroy()

        if file_path is None or file_path == "":
            self._importing = False
            return

        if not file_path.endswith(".svg"):
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror('Loading error', 'File is not of svg type')
            root.destroy()
            self._importing = False
            return

        # clear manual drawing
        self._layer.manual.clear()

        my_svg = svgelements.SVG.parse(file_path)

        # find the paths in the svgelement object file
        def unpack(svg_input, iteration):
            pathss = []
            if iteration != 5:
                if isinstance(svg_input, svgelements.Path):
                    pathss.append(svg_input)
                elif isinstance(svg_input, list):
                    for i in svg_input:
                        pathss.extend(unpack(i, iteration + 1))
            return pathss

        paths = unpack(my_svg, 0)

        if len(paths) == 0:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror('Loading error', 'SVG has no paths')
            root.destroy()
            self._importing = False
            return

        # get first list of points
        pre_points = []
        for path in paths:
            for element in path:

                # stop importing if requested
                if self._layer.g_u_i.quit_request:
                    return

                if isinstance(element, svgelements.Line) \
                        or isinstance(element, svgelements.QuadraticBezier) \
                        or isinstance(element, svgelements.CubicBezier):
                    pre_points.append(element.start)
                    pre_points.append(element.end)

        # get first limits of drawing
        minn = min([min(j.real, j.imag) for j in pre_points])
        maxx = max([max(j.real, j.imag) for j in pre_points])

        # get fuller list of points
        points = []
        for path in paths:
            for element in path:

                # stop importing if requested
                if self._layer.g_u_i.quit_request:
                    return

                if isinstance(element, svgelements.Line)\
                    or isinstance(element, svgelements.QuadraticBezier)\
                        or isinstance(element, svgelements.CubicBezier):
                    # get a list of points that make a curve
                    d = element.length()/((maxx-minn)/650)
                    for inter in range(int(d)):
                        points.append(element.point(inter / int(d)))

        # get better limits of drawing
        minn = min([min(j.real, j.imag) for j in points])
        maxx = max([max(j.real, j.imag) for j in points])

        # resize drawing to fit board
        def convx(x):
            return ((325 - (-325)) / (maxx - minn)) * (x - minn) - 325

        def convy(x):
            return ((325 - (-325)) / (maxx - minn)) * (x - minn) - 325

        ratio = (maxx-minn)/650

        # draw the paths using manual object
        for path_i in paths:

            # get font color
            def hsl_to_hsv(hsl):
                h, s, l = hsl
                h = h/360
                v = l + s * min(l, 1 - l)
                s = 0 if v == 0 else 2 * (1 - l / v)
                return h, s, v

            h1, s1, v1 = hsl_to_hsv(path_i.fill.hsl)

            self._manual.set_hue(h1)
            self._manual.set_sat(s1)
            self._manual.set_val(v1)

            # draw each element of the path
            for element in path_i:

                # stop importing if requested
                if self._layer.g_u_i.quit_request:
                    return

                els = []

                d = element.length()/ratio

                # get points from path function
                for inter in range(int(d)):
                    els.append(element.point(inter / int(d)))

                # add generated points to manual drawing list
                for el in els:
                    self._manual.increment((convx(el.real) + 1j * -convy(el.imag)))

        self._animation.update_time()
        self._animation.no_render()

        self._importing = False

    def exporting(self):
        """launch exporting"""

        if not self._exporting and self._animation.is_rendered()\
                and not self._layer.animation.asking() and not self._importing:

            self._exporting = True
            self.enable_exporting(False)
            self._manual.enable_clearing(False)
            self._animation.enable_speed(False)
            threading.Thread(target=self.exp).start()

    def exp(self):
        """Exports animation into mp4 format"""

        # Create temp directory if it does not exist
        if not os.path.exists("temp"):
            os.makedirs("temp")

        # Create temp directory if it does not exist
        if not os.path.exists("renders"):
            os.makedirs("renders")

        # get file output
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            defaultextension='.mp4', filetypes=[("mp4", '*.mp4')],
            initialdir="renders", initialfile='render.mp4',
            title="Choose filename")
        root.destroy()

        if file_path is None or file_path == "":
            self._exporting = False
            self.enable_exporting(True)
            self._manual.enable_clearing(True)
            self._animation.enable_speed(True)
            return

        frames = self._animation.frames()

        # generate temporary image files
        for i, frame in enumerate(frames):

            # stop exporting if requested
            if self._layer.g_u_i.quit_request:
                for filename in os.listdir("temp"):
                    file_path = os.path.join("temp", filename)
                    os.remove(file_path)
                return

            surf = pygame.Surface((self._layer.size[1], self._layer.size[1]))
            surf.fill(WHITE)
            surf.blit(frame, (0, 0))
            pygame.image.save(surf, os.path.join("temp", f"temp{i}.jpeg"))

            # display export percentage progress
            percent = str(int(50 * i / len(frames))) + "%"
            self._layer.layer_objects["label export%"].text = percent

        # Determine the width and height from the first image
        frame = cv2.imread(os.path.join("temp", "temp0.jpeg"))
        height, width, _ = frame.shape

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Be sure to use lower case
        out = cv2.VideoWriter(file_path, fourcc, 20.0, (width, height))

        # write the frames to the video file
        for i in range(len(frames)):

            # stop exporting if requested
            if self._layer.g_u_i.quit_request:
                out.release()
                # delete mp4 and temp images
                os.remove(file_path)
                for filename in os.listdir("temp"):
                    file_path = os.path.join("temp", filename)
                    os.remove(file_path)
                return

            frame = cv2.imread(os.path.join("temp", f"temp{i}.jpeg"))

            # Write out frame to video
            out.write(frame)

            # display export percentage progress
            percent = str(int(50+50 * i / len(frames))) + "%"
            self._layer.layer_objects["label export%"].text = percent

        self._layer.layer_objects["label export%"].text = "100%"

        # Release everything if job is finished
        out.release()

        # empty the temp folder
        for filename in os.listdir("temp"):
            file_path = os.path.join("temp", filename)
            os.remove(file_path)

        self._exporting = False
        self.enable_exporting(True)
        self._animation.enable_speed(True)
        self._manual.enable_clearing(True)

    def is_exporting(self):
        """getter"""

        return self._exporting

    def is_importing(self):
        """getter"""

        return self._importing

    def enable_exporting(self, value):
        """enables or disable exporting"""

        self._layer.layer_objects["click export"].disabled = not value

    def enable_importing(self, value):
        """enables or disable importing"""

        self._layer.layer_objects["click import"].disabled = not value

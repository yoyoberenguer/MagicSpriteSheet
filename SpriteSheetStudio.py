# encoding: utf-8

"""
MIT License

Copyright (c) 2021 Yoann Berenguer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Build CYTHON files
# In the main project directory :
# c:\>python setup_SpriteSheetStudio.py build_ext --inplace

# Make an executable file
#

import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter import IntVar, DoubleVar, StringVar, Label, LabelFrame, Button, Checkbutton, DISABLED, \
    NORMAL, RAISED, Entry, Scale, HORIZONTAL, FLAT, BooleanVar


import Pmw

try:
    import numpy

except ImportError:
    raise ImportError("Numpy library is not found on your system.\nplease try the following in a command prompt\n"
                      "C:>pip install numpy\n")
try:
    import pygame

except ImportError:
    raise ImportError("Pygame library is not found on your system.\nplease try the following in a command prompt\n"
                      "C:>pip install pygame\n")
from tkinter import colorchooser
import tkinter.font as tkFont
from tkinter import messagebox
import sys
import platform

try:
    from SpriteTools import blend_texture_32c, blend_texture_24_alpha, \
    swap_channels24_c, \
    horizontal_glitch32, horizontal_glitch24, \
    invert_surface_24bit, invert_surface_24bit_exclude, invert_surface_32bit, swap_channels32_c, vertical_glitch24_c, \
    blend_to_textures_24c, blend_to_textures_32c, greyscale_lightness24_c, sobel24, median_filter24_c, \
    color_reduction24_c, greyscale_luminosity24_c, greyscale24_c, vertical_glitch32_c, greyscale_lightness32_c, \
    greyscale_luminosity32_c, greyscale32_c, median_filter32_c, color_reduction32_c, sobel32, dithering24_c, \
    dithering32_c, pixelate24, pixelate32, create_pixel_blocks_rgba, sepia24_c, create_pixel_blocks_rgb, \
    invert_surface_32bit_exclude

except ImportError:
    raise ImportError("SpriteTools library is not found for on system.\n"
                      "Go into the project main directory and type the following in a command prompt \n"
                      "C:>python setup_SpriteSheetStudio.py build_ext --inplace\n")

try:
    from GaussianBlur5x5 import canny_blur5x5_surface24_c, canny_blur5x5_surface32_c
except ImportError:
    raise ImportError("GaussianBlur5x5 library is not found on your system.\n"
                      "Go into the project main directory and type the following in a command prompt \n"
                      "C:>python setup_SpriteSheetStudio.py build_ext --inplace\n")

from RGB_split import rgb_split_channels, rgb_split_channels_alpha

try:
    from Saturation import saturation_array32, saturation_array24

except ImportError:
    raise ImportError("Saturation library is not found on your system.\n"
                      "Go into the project main directory and type the following in a command prompt \n"
                      "C:>python setup_SpriteSheetStudio.py build_ext --inplace\n")
try:
    from bloom import bloom_effect_array32, bloom_effect_array24, blur5x5_array32, blur5x5_array24

except ImportError:
    raise ImportError("bloom library is not found on your system.\n"
                      "Go into the project main directory and type the following in a command prompt \n"
                      "C:>python setup_SpriteSheetStudio.py build_ext --inplace\n")

try:
    from hsv_surface import hsv_surface24c, hsv_surface32c

except ImportError:
    raise ImportError("hsv_surface library is not found on your system.\n"
                      "Go into the project main directory and type the following in a command prompt \n"
                      "C:>python setup_SpriteSheetStudio.py build_ext --inplace\n")

import os
from os.path import basename

try:
    import PIL
    from PIL import Image, ImageTk
except ImportError:
    raise ImportError("pillow library is not found on your system.\nplease try the following in a command prompt\n"
                      "C:>pip install pygame\n")

try:
    from SpriteSheet import sprite_sheet_per_pixel, sprite_sheet

except ImportError:
    raise ImportError("SpriteSheet library is not found on your system.\n"
                      "Go into the project main directory and type the following in a command prompt \n"
                      "C:>python setup_SpriteSheetStudio.py build_ext --inplace\n")

icon = pygame.image.load("Assets\\magma.ico")
pygame.display.set_icon(icon)
SCREEN = pygame.display.set_mode((600, 600))
VERSION = 1.00
SCREEN_WIDTH = 1465
SCREEN_HEIGHT = 800
BUFFER_TKINTER_OPTIONS = {}
BUFFER_TKINTER_CHECKBOX = {}
LABEL = None


class GL(tkinter.Frame):
    """
    GLOBAL PROGRAM VARIABLE/CONSTANT
    """

    def __init__(self):
        tkinter.Frame.__init__(self)

        # BACKGROUND COLOR
        self.background_color = "#858585"
        # DEFAULT LABEL TEXT BACKGROUND COLOR
        self.bkcolor = "#858585"

        # FILE PATH
        self.path = "/"
        # SPRITESHEET FILE EXTENSION ALLOWED
        # JPG
        # PNG
        # GIF (non-animated)
        # BMP
        # PCX
        # TGA (uncompressed)
        # TIF
        # LBM (and PBM)
        # PBM (and PGM, PPM)
        # XPM
        self.file_format = (("PNG files", "*.png"), ("JPEG files", "*.jpg"),
                            ("GIF (non animated)", "*.gif"), ("BMP files", "*.bmp"),
                            ("PCX files", "*.pcx"), ("TGA uncompressed", "*.tga"),
                            ("TIF files", "*.tif"), ("LBM (and PBM", "*.lbm"),
                            ("PBM files", "*.pbm"), ("XPM files", "*.xpm"),
                            ("all files", "*.*"))

        global VERSION
        self.title = "SpriteSheet Studio version %s" % VERSION

        # CHECKER BACKGROUND IMAGE TO USE FOR 32-BIT SURFACE
        # DEFAULT SIZE 600x600
        self.checker_background = pygame.image.load("Assets\\background.png")
        self.checker_background = pygame.transform.smoothscale(self.checker_background, (600, 600))

        # LIST CONTAINING ALL THE PYGAME SURFACES (IMAGE LOADED AFTER PROCESSING THE
        # SPRITESHEET. THE TRANSFORMATION (BLEND, BLUR ETC WILL BE APPLIED TO ALL TEXTURES
        # IN THE LIST PYIMAGE)
        self.pyimage = []

        # LIST CONTAINING THE TKINTER IMAGES TO DISPLAY ON CANVAS
        self.tkimage = []

        # DEFAULT TKINTER IMAGE DISPLAY FOR THE EDIT COLOR BUTTON (COLOR GRADIENT)
        # IMAGE SIZE 20x20
        self.color_icon = Image.open(r"Assets\\EditColor.png")
        self.color_icon = self.color_icon.resize((20, 20), Image.ANTIALIAS)
        self.color_icon = ImageTk.PhotoImage(self.color_icon)

        # DEFAULT TKINTER IMAGE DISPLAY BY THE LABEL PREVOEW (64x64)
        self.preview_image = Image.open(r"Assets\\python logo.png")
        self.preview_image = self.preview_image.resize((64, 64), Image.ANTIALIAS)
        self.preview_image = ImageTk.PhotoImage(self.preview_image)

        # PADLOCK TKINTER IMAGE TO USE WHEN SIZE WIDTH AND HEIGHT ARE INDENTICAL (LOCKED)
        # DEFAULT SIZE 16x16
        self.padlock_lock_image = Image.open(r"Assets\\Lock.png")
        self.padlock_lock_image = self.padlock_lock_image.resize((16, 16), Image.ANTIALIAS)
        self.padlock_lock_image = ImageTk.PhotoImage(self.padlock_lock_image)

        # UNLOCK IMAGE
        self.padlock_unlock_image = Image.open(r"Assets\\Lock-Unlock-icon.png")
        self.padlock_unlock_image = self.padlock_unlock_image.resize((16, 16), Image.ANTIALIAS)
        self.padlock_unlock_image = ImageTk.PhotoImage(self.padlock_unlock_image)

        # GLARE EFFECT TEXTURE DEFAULT (IMAGE TO DISPLAY ON LABEL DEFAULT SIZE 64x64
        self.glow_shape = Image.open(r"Assets\\icon_glareFx_red.png")
        self.glow_shape = self.glow_shape.resize((64, 64), Image.ANTIALIAS)
        self.glow_shape = ImageTk.PhotoImage(self.glow_shape)

        # GLARE EFFECT TEXTURE TO BLEND WITH ALL PYGAME IMAGE (PYIMAGE_)
        self.glow_shape_pygame = pygame.image.load(
            "Assets\\icon_glareFx_red.png").convert()
        self.glow_shape_pygame = pygame.transform.smoothscale(self.glow_shape_pygame, (64, 64))

        # TRANSITION TEXTURE FOR TRANSITION EFFECT (EMPTY SURFACE SIZE 10x10)
        self.transition_texture = pygame.Surface((10, 10), pygame.SRCALPHA)

        # TKINTER VARIABLES
        self.rows_value = IntVar()
        self.columns_value = IntVar()
        self.input_format_32bit = IntVar()
        self.input_format_24bit = IntVar()
        self.width_value = IntVar()
        self.height_value = IntVar()
        self.spritesheet_name_variable = StringVar()
        self.red = IntVar()
        self.green = IntVar()
        self.blue = IntVar()
        self.exclude_red = IntVar()
        self.exclude_green = IntVar()
        self.exclude_blue = IntVar()
        self.colorkey_red = IntVar()
        self.colorkey_green = IntVar()
        self.colorkey_blue = IntVar()
        self.padlock_status = "locked"
        self.rgbsplitxoffset = StringVar()
        self.rgbsplityoffset = StringVar()
        self.blend_start_frame = IntVar()
        self.blend_end_frame = IntVar()
        self.hsvstart_frame = IntVar()
        self.hsvend_frame = IntVar()
        self.bloomstart_frame = IntVar()
        self.bloomend_frame = IntVar()
        self.rgbsplit_start_frame = IntVar()
        self.rgbsplit_end_frame = IntVar()
        self.transition_start_frame = IntVar()
        self.transition_end_frame = IntVar()
        self.glitch_start_frame = IntVar()
        self.glitch_end_frame = IntVar()
        self.blend_scale_percentage = DoubleVar()
        self.output_format_24bit = BooleanVar()
        self.output_format_32bit = BooleanVar()
        self.rleaccel_value = BooleanVar()
        self.set_alpha_value = BooleanVar()
        self.colorkey = BooleanVar()
        self.hsv_checkbox = BooleanVar()
        self.hsv_scale_value = DoubleVar()
        self.hsv_rotate = BooleanVar()
        self.bloom_checkbox = BooleanVar()
        self.highpass_filter_value = DoubleVar()
        self.preview_scale_delay = IntVar()
        self.checker_value = BooleanVar()
        self.inverse_variable = BooleanVar()
        self.saturation_checkbox = BooleanVar()
        self.saturation_scale_value = DoubleVar()
        self.cartoon_checkbox = BooleanVar()
        self.blur_checkbox = BooleanVar()
        self.blur_progressive = BooleanVar()
        self.blurx2 = BooleanVar()
        self.blurx4 = BooleanVar()
        self.blurx6 = BooleanVar()
        self.blurstart_frame = IntVar()
        self.blurend_frame = IntVar()
        self.glow_checkbox = BooleanVar()
        self.glow_var = StringVar()
        self.glow_scale_value = DoubleVar()
        self.channel_checkbox = BooleanVar()
        self.widget_var = StringVar()
        self.red_channel = BooleanVar()
        self.green_channel = BooleanVar()
        self.blue_channel = BooleanVar()
        self.split_blue_checkbox = BooleanVar()
        self.split_green_checkbox = BooleanVar()
        self.split_red_checkbox = BooleanVar()
        self.rgbsplit_checkbox = BooleanVar()
        self.transition_checkbox = BooleanVar()
        self.transition_alpha1 = BooleanVar()
        self.transition_alpha2 = BooleanVar()
        self.glitch_checkbox = BooleanVar()
        self.glitch_horizontal = BooleanVar()
        self.glitch_vertical = BooleanVar()
        self.exclude_red_inv = IntVar()
        self.exclude_green_inv = IntVar()
        self.exclude_blue_inv = IntVar()
        self.inverse_exclude_variable = BooleanVar()
        self.width_entry_variable = IntVar()
        self.height_entry_variable = IntVar()
        self.cartoon_lightness = BooleanVar()
        self.cartoon_luminosity = BooleanVar()
        self.cartoon_average = BooleanVar()
        self.cartoon_threshold = IntVar()
        self.cartoon_neightboors = IntVar()
        self.cartoon_color = IntVar()
        self.pixel = BooleanVar()
        self.pixel_size = IntVar()
        self.greyscale = BooleanVar()
        self.sepia = BooleanVar()
        self.dithering = BooleanVar()
        self.dithering_value = IntVar()
        self.output_width_value = IntVar()
        self.output_height_value = IntVar()
        self.output_rows_value = IntVar()
        self.output_columns_value = IntVar()
        self.file_format_value = StringVar()
        self.glow_direction = None

        self.file_format_value.set("PNG")
        self.pixel_size.set(8)
        self.cartoon_lightness.set(0)
        self.cartoon_luminosity.set(0)
        self.cartoon_average.set(1)
        self.cartoon_threshold.set(20)
        self.cartoon_neightboors.set(4)
        self.cartoon_color.set(16)
        self.green_channel.set(1)
        self.blue_channel.set(1)
        self.red_channel.set(1)
        self.glow_scale_value.set(0.0)
        self.blurend_frame.set(100)
        self.blurstart_frame.set(0)
        self.blurx6.set(0)
        self.blurx4.set(0)
        self.blurx2.set(0)
        self.blur_progressive.set(0)
        self.blur_checkbox.set(0)
        self.cartoon_checkbox.set(0)
        self.saturation_scale_value.set(0)
        self.saturation_checkbox.set(0)
        self.inverse_variable.set(0)
        self.checker_value.set(1)
        self.preview_scale_delay.set(60)
        self.highpass_filter_value.set(128)
        self.bloom_checkbox.set(0)
        self.hsvstart_frame.set(0)
        self.hsvend_frame.set(100)
        self.hsv_rotate.set(0)
        self.hsv_scale_value.set(0.0)
        self.hsv_checkbox.set(0)
        self.colorkey.set(0)
        self.set_alpha_value.set(0)
        self.rleaccel_value.set(0)
        self.output_format_32bit.set(0)
        self.output_format_24bit.set(0)
        self.blend_scale_percentage.set(0.0)
        self.glitch_end_frame.set(100)
        self.glitch_start_frame.set(0)
        self.transition_end_frame.set(100)
        self.transition_start_frame.set(0)
        self.rgbsplit_end_frame.set(100)
        self.rgbsplit_start_frame.set(0)
        self.bloomend_frame.set(100)
        self.bloomstart_frame.set(0)
        self.blurend_frame.set(100)
        self.blurstart_frame.set(0)
        self.hsvend_frame.set(100)
        self.blend_end_frame.set(100)
        self.blend_start_frame.set(0)
        self.input_format_24bit.set(1)
        self.width_value.set(512)
        self.height_value.set(512)
        self.spritesheet_name_variable.set("")
        self.rgbsplitxoffset.set(10)
        self.rgbsplityoffset.set(10)
        self.split_red_checkbox.set(1)
        self.split_green_checkbox.set(1)
        self.split_blue_checkbox.set(1)
        self.glitch_checkbox.set(0)
        self.exclude_red_inv.set(0)
        self.exclude_green_inv.set(0)
        self.exclude_blue_inv.set(0)
        self.inverse_exclude_variable.set(0)

        # ROOT WINDOW GEOMETRY
        self.x_offset = 100
        self.y_offset = 100

        global SCREEN_WIDTH, SCREEN_HEIGHT

        self.geometry = str(SCREEN_WIDTH) + "x" + str(SCREEN_HEIGHT) + "+" \
            + str(self.x_offset) + "+" + str(self.y_offset)

        self.cancel = False

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result


def pygame_to_tkinter(pygame_surface_, width_: int, height_: int) -> (ImageTk.PhotoImage, None):
    """
    TRANSFORM A PYGAME IMAGE INTO A TKINTER  PHOTOIMAGE TYPE, SIZE WIDTH & HEIGHT

    :param pygame_surface_: pygame surface
    :param width_         : integer; Tkinter final surface width
    :param height_        : integer; tkinter final surface height
    :return: Return a tkinter PhotoImage type image or return None if image cannot be converted
    """
    try:
        pygame_surface_ = pygame.transform.smoothscale(pygame_surface_, (width_, height_))
        image_str = pygame.image.tostring(pygame_surface_, 'RGBA')
        image = Image.frombytes('RGBA', (width_, height_), image_str)

    except Exception as error_code:
        messagebox.showerror(
            "Error", "Pygame image cannot be converted to Tkinter PhotoImage type\n"
                     "Error returned: %s " % error_code)
        return None
    return ImageTk.PhotoImage(image)


def tkinter_to_pygame(tkinter_surface_, width_: int, height_: int) -> (pygame.Surface, None):
    """
    TRANSFORM A TKINTER PHOTOIMAGE INTO A PYGAME SURFACE OF SIZE WIDTH AND HEIGHT

    :param tkinter_surface_: Take a Tkinter PhotoImage as input
    :param width_          : integer; Final Pygame image width
    :param height_         : integer; Final Pygame image height
    :return: Return a Pygame image of size width & height, image format RGBA or return None if failed to convert
    the image
    """
    try:
        image_string = ImageTk.getimage(tkinter_surface_)

    except Exception as error_code:
        messagebox.showerror(
            "Error", "Tkinter PhotoImage cannot be converted to Pygame surface type\n"
                     "Error returned : %s " % error_code)
        return None
    return pygame.image.frombuffer(image_string.tobytes(), (width_, height_), "RGBA")


def validate_data(s):
    return s.isdigit()


def dummy():
    pass


def select_color(red_, green_, blue_) -> None:
    """
    SET TKINTER COLOR VARIABLE (RED, GREEN, BLUE) RETURNED BY THE COLOR EDIT MENU (colorchooser)

    :param red_: InteVar; tkinter IntVar variable; red color return by the edit menu
    :param green_: InteVar; tkinter IntVar variable; green color return by the edit menu
    :param blue_: InteVar; tkinter IntVar variable; blue color return by the edit menu
    :return: None
    """
    if type(red_).__name__ != "IntVar":
        raise ValueError("Argument red_ is not a tkinter DoubleVar")
    if type(green_).__name__ != "IntVar":
        raise ValueError("Argument green_ is not a tkinter DoubleVar")
    if type(blue_).__name__ != "IntVar":
        raise ValueError("Argument blue_ is not a tkinter DoubleVar")

    color_struct = colorchooser.askcolor()

    if color_struct is not None:
        if isinstance(color_struct, tuple) and color_struct[0] is not None:
            red = int(color_struct[0][0])
            if red is not None:
                red_.set(red)

            green = int(color_struct[0][1])
            if green is not None:
                green_.set(green)

            blue = int(color_struct[0][2])
            if blue is not None:
                blue_.set(blue)


# noinspection PyBroadException
class SpriteSheetStudio:

    def __init__(self, root_, gl_):
        self.gl = gl_
        self.root = root_
        self.root.withdraw()
        # MAIN WINDOW IS FULLY TRANSPARENT
        self.root.attributes('-alpha', 0.0)
        # root.wm_iconbitmap()
        self.root.geometry(gl_.geometry)
        self.root.title(gl_.title)
        self.draw_menu()

        # INPUT OPTIONS WIDGETS
        self.input_options = None
        self.width_entry = None
        self.height_entry = None
        self.padlock_button = None

        # OUTPUT OPTIONS WIDGETS
        self.output_option = None

        # BLEND WIDGETS
        self.blend_checkbox = None
        self.exclude_red_entry = None
        self.exclude_green_entry = None
        self.exclude_blue_entry = None
        self.exclude_button = None

        self.effect_labelframe = None
        self.bloom_preview = None
        self.empty = None
        self.preview_delay_value = None
        self.checker_background_value = None
        self.hsv_preview = None
        self.blur_preview = None
        self.saturation_preview = None
        self.glow_shape_preview = None
        self.channel_conversion = None
        self.rgb_channel_preview = None
        self.rgbsplit_preview = None
        self.transition_texture = None
        self.transition_preview = None
        self.glitch_preview = None
        self.preview_button = None
        self.format_24bit = None
        self.format_32bit = None
        self.animation_canvas = None
        # LABEL WIDGET SHOWING THE AMOUNT OF FRAMES
        self.frame_number = None
        self.duration = None
        self.preview_labelframe = None
        self.exclude_button_inv = None
        self.output_width = None
        self.output_height = None
        self.pyimage_copy = None
        self.save_button = None
        self.rgb_split = None

        self.input_settings()
        self.output_options()
        self.blending_effect()
        self.hsv_effect()
        self.preview_options()
        self.effects_frame()
        self.canvas_preview()
        self.bloom_effect()
        self.saturation_effect()
        self.cartoon_effect()
        self.blur_effect()
        self.glow_effect()
        self.rgb_channel_effect()
        self.rgb_split_effect()
        self.transition_effect()
        self.glitch_effect()
        self.miscelleanous_effect()


    def save_spritesheet(self):

        self.save_button.config(state="disabled")

        file_format = str(self.gl.file_format_value.get())
        file_format_ = [(file_format + " files", "*." + file_format.lower())]

        filename = None

        try:
            filename = filedialog.asksaveasfile(
                initialdir=self.gl.path, title="Save as", filetypes=file_format_, defaultextension=file_format_)
        except Exception as e:
            messagebox.showerror("Error", "Cannot save the spritesheet in the current directory.\n"
                                          "Error : %s " % e)
            self.save_button.configure(state="normal")
            return

        if filename is None:
            self.save_button.configure(state="normal")
            return

        try:
            try:
                rows = self.gl.output_rows_value.get()
            except:
                raise ValueError("Output row value is incorrect.")

            try:
                columns = self.gl.output_columns_value.get()
            except:
                raise ValueError("Output column calue is incorrect.")

            if self.pyimage_copy is not None and isinstance(self.pyimage_copy, list):
                if rows * columns != len(self.pyimage_copy):
                    raise ValueError("Rows or Columns value(s) does not match the number of sprites to write.")
                width, height = self.pyimage_copy[0].get_size()
            else:
                raise ValueError("Please load a spritesheet first!")

            try:
                new_width = self.gl.output_width_value.get()
                if new_width == 0:
                    raise ValueError
            except:
                new_width = width

            try:
                new_height = self.gl.output_height_value.get()
                if new_height == 0:
                    raise ValueError
            except:
                new_height = height

            i = 0
            if new_width != width or new_height != height:
                for sprite in self.pyimage_copy:
                    self.pyimage_copy[i] = pygame.transform.smoothscale(sprite, (new_width, new_height))
                    i += 1

            width, height = self.pyimage_copy[0].get_size()

            spritesheet_width = width * columns
            spritesheet_height = height * rows

            format = None
            if bool(self.gl.input_format_32bit.get()):
                # FOR 32bit
                new_surface = pygame.Surface((width * columns, height * rows), pygame.SRCALPHA)
                new_surface.convert_alpha()
                new_surface.fill((0, 0, 0, 0))
                format = 32
            elif bool(self.gl.input_format_24bit.get()):
                # FOR 24BIT
                new_surface = pygame.Surface((spritesheet_width, spritesheet_height))
                new_surface.convert()
                new_surface.fill((0, 0, 0))
                format = 24

            ii = 0
            jj = 0
            for sprite in self.pyimage_copy:

                new_surface.blit(sprite, (ii, jj))
                ii += width
                if ii >= width * columns:
                    jj += height
                    ii = 0
            try:
                red = self.gl.colorkey_red.get()
            except:
                red = None
            try:
                green = self.gl.colorkey_green.get()
            except:
                green = None
            try:
                blue = self.gl.colorkey_blue.get()
            except:
                blue = None

            alpha = 25

            if bool(self.gl.colorkey.get()):
                if bool(self.gl.input_format_24bit.get()):

                    if bool(self.gl.rleaccel_value.get()):
                        if red is not None and green is not None and blue is not None:
                            new_surface.set_colorkey((red, green, blue), pygame.RLEACCEL)
                    else:
                        if red is not None and green is not None and blue is not None:
                            new_surface.set_colorkey((red, green, blue))

            if bool(self.gl.set_alpha_value.get()):
                new_surface.set_alpha(alpha)

            # CLOSE THE FILE BEFORE WRITING THE IMAGE
            filename.close()
            try:
                pygame.image.save(new_surface, os.path.join("", filename.name))

            except Exception as e:
                messagebox.showerror(
                    "Error", "Spritesheet: %s cannot be save to the destination:\n"
                             "%s\n\n"
                             "Details:\n"
                             "format: %s\n"
                             "size: %sx%s\n"
                             "bitsize: %s\n\n"
                             "Error code : %s " % (filename.name, self.gl.path,
                                                   file_format, str(width), str(height), format, e))
        except Exception as error:

            messagebox.showerror(
                "Error", "An error occur during the Spritesheet creation!\n"
                         " Error: %s " % error)
        finally:
            self.save_button.configure(state="normal")

    def update_canvas(self, image_: PIL.ImageTk.PhotoImage) -> None:
        """
        UPDATE THE PREVIEW CANVAS AND DISPLAY THE SPRITESHEET ANIMATION

        :param image_: tkinter image; List of image to be display on the canvas
        :return: None
        """
        if not isinstance(image_, PIL.ImageTk.PhotoImage):
            raise TypeError("Argument image_ must be a tkinter PhotoImage type got %s " % type(image_))

        assert self.gl.checker_background is not None, "checker_background image cannot be None"
        assert self.animation_canvas.winfo_exists(), "Animation canvas widget does not exists"
        checker: bool = self.gl.checker_value.get()
        global LABEL
        # IMAGE IS SCALE TO 256x256 (CANVAS SIZE)
        if checker:
            im = pygame_to_tkinter(self.gl.checker_background, 256, 256)
            self.animation_canvas.create_image(0, 0, image=im, anchor=tkinter.NW)
            LABEL = Label(self.root, image=im)
            LABEL.image = im  # keep a reference!
        self.animation_canvas.create_image(0, 0, image=image_, anchor=tkinter.NW, tags="preview")
        LABEL = Label(self.root, image=image_)
        LABEL.image = image_  # keep a reference!
        self.animation_canvas.update_idletasks()
        self.animation_canvas.update()

    def refresh(self, sprite_: pygame.Surface) -> None:
        """
        DISPLAY THE SPRITESHEET ANIMATION IN A PYGAME DISPLAY

        * Optionally the animation will be played on a background image (checker)
        * Animation is played without blending attributes

        :param sprite_: pygame.Surface;
        :return: None
        """
        global SCREEN

        if not isinstance(sprite_, pygame.Surface):
            raise TypeError("Argument sprite_ must be a list containing pygame surfaces got %s" % type(sprite_))

        assert self.gl.checker_background is not None, "checker_background image cannot be None"

        checker: bool = self.gl.checker_value.get()

        if pygame.display.get_init() and SCREEN is not None:

            SCREEN.fill((0, 0, 0, 0))
            if checker:
                SCREEN.blit(self.gl.checker_background, (0, 0))
            SCREEN.blit(sprite_, (0, 0))
            pygame.event.pump()
            pygame.display.flip()
        else:
            raise ValueError(
                " Pygamne display has not been initialized correctly.\n"
                " Please restart MagicSprite Studio or re-install the program from windows installer.")

    def canvas_preview(self) -> None:
        """
        CREATE THE TKINTER CANVAS FOR SPRITESHEET ANIMATION (CANVAS SIZE IS 256 x 256)
        :return: None
        """
        self.preview_labelframe = tkinter.LabelFrame(
            self.effect_labelframe, text="Preview window", bg="#858585", width=475, height=400, bd=2)
        self.preview_labelframe.place(x=480, y=490)

        self.animation_canvas = tkinter.Canvas(self.preview_labelframe, bg="BLACK", width=256, height=256)
        self.animation_canvas.place(x=5, y=5)

        self.save_button = tkinter.Button(
            self.preview_labelframe, text="Save", width=6, bg=self.gl.background_color,
            relief=RAISED, command=self.save_spritesheet)
        self.save_button.place(x=300, y=50)
        self.save_button.config(state=DISABLED)

    def open_spritesheet(self) -> None:
        """
        OPEN A GIVEN SPRITESHEET WITH THE GIVEN TKINTER VARIABLES
        + width
        + height
        + rows
        + columns
        + 24-bit or 32-bit

         IF THE SPRITESHEET FAIL TO OPEN, AN ERROR MESSAGE WILL BE DISPLAY ON THE SCREEN.
         IF VARIABLE(S) ARE INCORRECT TYPE OR RANGE AN ERROR MESSAGE WILL ALSO BE DISPLAY.

        JPG
        PNG
        GIF (non-animated)
        BMP
        PCX
        TGA (uncompressed)
        TIF
        LBM (and PBM)
        PBM (and PGM, PPM)
        XPM

        :return: None
        """

        try:
            filename = filedialog.askopenfilename(
                initialdir=self.gl.path, title="Select a spritesheet", filetypes=self.gl.file_format)
        except:
            messagebox.showerror("Error", "Cannot open the current directory or spritesheet.")
            return

        name = basename(filename)
        if name is not None and name != "":

            try:
                width = self.width_entry.get()
                if width == "0":
                    raise ValueError
            except:
                messagebox.showinfo("Info", "Sprite width value is invalid.")
                return

            try:
                height = self.height_entry.get()
                if height == "0":
                    raise ValueError
            except:
                messagebox.showinfo("Info", "Sprite height value is invalid.")
                return

            if not width.isnumeric():
                messagebox.showerror(
                    "Info", "Sprite size, width value is invalid.\nExpecting an integer value got %s" % type(width))
                return
            if not height.isnumeric():
                messagebox.showerror(
                    "Info", "Sprite size, height value is invalid.\nExpecting an integer value got %s" % type(height))
                return

            if self.gl.padlock_status == "unlocked":

                try:
                    height = self.gl.height_entry.get()
                except:
                    messagebox.showinfo("Info", "Sprite height value is invalid.")
                    return

                if not width.isnumeric():
                    messagebox.showerror(
                        "Info",
                        "Sprite size, height value is invalid.\nExpecting an integer value got %s" % type(height))
                    return

            try:
                rows = self.gl.rows_value.get()
            except:
                messagebox.showinfo("Info", "Sprite rows value is invalid.")
                return

            if not isinstance(rows, int):
                messagebox.showerror(
                    "Info", "Rows value is invalid.\nExpecting an integer value got %s" % type(rows))
                return
            try:
                columns = self.gl.columns_value.get()
            except:
                messagebox.showinfo("Info", "Sprite columns value is invalid.")
                return

            if not isinstance(columns, int):
                messagebox.showerror(
                    "Info", "Columns value is invalid.\nExpecting an integer value got %s" % type(columns))
                return

            if self.gl.input_format_24bit.get() == 1:
                try:

                    sprites = sprite_sheet(filename, chunk_=int(width), rows_=int(rows), columns_=int(columns))
                except Exception as error:
                    messagebox.showerror(
                        "Error", "Fail to open spritesheet %s\nError code : %s" % (filename, error))
                    return
            else:
                try:
                    sprites = sprite_sheet_per_pixel(filename, chunk_=int(width), rows_=int(rows),
                                                     columns_=int(columns))
                except Exception as error:
                    messagebox.showerror(
                        "Error", "Fail to open spritesheet %s\nError code : %s" % (filename, error))
                    return

            if sprites is None:
                return

            if not isinstance(sprites, list) or len(sprites) == 0:
                return

            # # todo try except for each colors
            # if bool(self.gl.colorkey.get()):
            #     for surface in sprites:
            #         surface.set_colorkey(
            #             (int(self.gl.colorkey_red.get()),
            #              int(self.gl.colorkey_green.get()),
            #              int(self.gl.colorkey_blue.get())), pygame.RLEACCEL if bool(self.gl.rleaccel_value.get()) else
            #         0)
            #
            # elif bool(self.gl.set_alpha_value.get()):
            #     for surface in sprites:
            #         surface.set_alpha(128, pygame.RLEACCEL if bool(self.gl.rleaccel_value.get()) else 0)

            w, h = sprites[0].get_size()
            pygame.display.set_mode((w, h))

            self.animation_canvas.delete('all')
            self.gl.tkimage = []
            if self.gl.input_format_24bit.get():
                # BUILD THE TKINTER CANVAS ANIMATION
                for surf in sprites:
                    surf = pygame.transform.smoothscale(surf, (256, 256))
                    image_str = pygame.image.tostring(surf, 'RGB')  # use 'RGB' to export
                    w, h = surf.get_rect()[2:]
                    image = Image.frombytes('RGB', (w, h), image_str)
                    tk_image = ImageTk.PhotoImage(image)  # use ImageTk.PhotoImage class instead
                    self.gl.tkimage.append(tk_image)
            else:
                for surf in sprites:
                    surf = pygame.transform.smoothscale(surf, (256, 256))
                    image_str = pygame.image.tostring(surf, 'RGBA')
                    w, h = surf.get_rect()[2:]
                    image = Image.frombytes('RGBA', (w, h), image_str)
                    tk_image = ImageTk.PhotoImage(image)  # use ImageTk.PhotoImage class instead
                    self.gl.tkimage.append(tk_image)

            i = 0
            for _ in self.gl.tkimage:
                self.animation_canvas.delete('all')
                self.update_canvas(self.gl.tkimage[i % len(sprites)])
                self.refresh(sprites[i % len(sprites)])
                pygame.time.delay(16)
                i += 1

            self.gl.pyimage = sprites

            length = len(sprites)
            self.gl.blend_start_frame.set(0)
            self.gl.blend_end_frame.set(length)
            self.gl.hsvstart_frame.set(0)
            self.gl.hsvend_frame.set(length)
            self.gl.blurstart_frame.set(0)
            self.gl.blurend_frame.set(length)
            self.gl.bloomstart_frame.set(0)
            self.gl.bloomend_frame.set(length)
            self.gl.spritesheet_name_variable.set(name)
            self.gl.rgbsplit_start_frame.set(0)
            self.gl.rgbsplit_end_frame.set(length)
            self.gl.transition_start_frame.set(0)
            self.gl.transition_end_frame.set(length)
            self.gl.glitch_start_frame.set(0)
            self.gl.glitch_end_frame.set(length)
            self.gl.output_width_value.set(self.width_entry.get())
            self.gl.output_height_value.set(self.height_entry.get())
            self.gl.output_rows_value.set(self.gl.rows_value.get())
            self.gl.output_columns_value.set(self.gl.columns_value.get())
            self.gl.output_format_24bit.set(self.gl.input_format_24bit.get())
            self.gl.output_format_32bit.set(self.gl.input_format_32bit.get())

            if self.gl.input_format_32bit.get():
                self.exclude_red_entry.config(state=DISABLED)
                self.exclude_green_entry.config(state=DISABLED)
                self.exclude_blue_entry.config(state=DISABLED)
                self.exclude_button.config(state=DISABLED)
            else:
                self.exclude_red_entry.config(state=NORMAL)
                self.exclude_green_entry.config(state=NORMAL)
                self.exclude_blue_entry.config(state=NORMAL)
                self.exclude_button.config(state=NORMAL)

            self.bloom_preview_update(self.gl.highpass_filter_value.get())
            self.hsv_preview_update(self.gl.hsv_scale_value.get())
            self.saturation_preview_update(self.gl.saturation_scale_value.get())
            self.channels_preview_update()
            self.rgb_split_preview_update()
            self.blur_effect_preview_update()
            self.frame_number.config(text=str(length))
            self.save_button.config(state=NORMAL)
            self.preview_button.config(state=NORMAL)

            try:
                ms = self.gl.preview_scale_delay.get()
                t = round(((1 / ms) * length), 3)
                self.duration.config(text=str(t))

            except:
                # FORCE THE VALUE IF THE SCALE WIDGET IS REPORTING AN INVALID VALUE
                self.duration.config(text="0.0")

            if bool(self.gl.input_format_32bit.get()):
                self.rgb_split.configure(state=DISABLED)
            else:
                self.rgb_split.configure(state=NORMAL)

    def tickbox_24bit(self) -> None:
        """
        CHECK THE TICK BOX 24-BIT FOR IMAGE FORMAT.
        WHEN THE VARIABLE input_format_24bit is set, input_format_32bit WILL AUTOMATICALLY
        BE DESELECTED

        :return: None
        """
        if self.gl.input_format_32bit.get() == 1 and self.gl.input_format_24bit.get() == 1:
            self.gl.input_format_32bit.set(0)
            # self.input_red.config(state=NORMAL)
            # self.input_green.config(state=NORMAL)
            # self.input_blue.config(state=NORMAL)
            # self.input_setalpha.config(state=NORMAL)
            # self.input_colorkey.config(state=NORMAL)
            # self.input_colorkey_edit.config(state=NORMAL)
            # self.input_rleaccel.config(state=NORMAL)

    def tickbox_32bit(self) -> None:
        """
        CHECK THE TICK BOX 24-BIT FOR IMAGE FORMAT.
        WHEN THE VARIABLE input_format_32bit is set, input_format_24bit WILL AUTOMATICALLY
        BE DESELECTED

        :return: none
        """
        if self.gl.input_format_24bit.get() == 1 and self.gl.input_format_32bit.get() == 1:
            self.gl.input_format_24bit.set(0)
            # self.input_red.config(state=DISABLED)
            # self.input_green.config(state=DISABLED)
            # self.input_blue.config(state=DISABLED)
            # self.input_setalpha.config(state=DISABLED)
            # self.input_colorkey.config(state=DISABLED)
            # self.input_colorkey_edit.config(state=DISABLED)
            # self.input_rleaccel.config(state=DISABLED)

    def padlock(self) -> None:
        """
        CHECK THE PADLOCK STATUS (WIDTH ADN HEIGHT PADLOCK) AND CHANGE THE PADLOCK IMAGE
        FROM LOCK TO UNLOCK AND VICE VERSA

        :return: None
        """
        assert self.gl.padlock_unlock_image is not None, "Unlock padlock image does not exists or has not been set."
        assert self.gl.padlock_lock_image is not None, "Lock padlock image does not exists or has not been set."

        if self.padlock_button.cget('image') == 'pyimage3':
            self.padlock_button.config(image=self.gl.padlock_unlock_image)
            self.gl.padlock_status = "unlocked"

        else:

            self.padlock_button.config(image=self.gl.padlock_lock_image)
            self.gl.padlock_status = "locked"

            try:
                w = self.gl.width_entry_variable.get()
                self.height_entry.delete(0, tkinter.END)
                self.height_entry.insert(0, w)

            except Exception as error:
                messagebox.showwarning("Warning", "The sprite width value is invalid.\nError : %s" % error)
                return

    def input_settings(self):
        self.input_options = tkinter.LabelFrame(
            self.root, text="INPUT settings", bg="#858585", width=475, height=170, bd=2)
        self.input_options.place(x=5, y=5)

        size_labelframe = tkinter.LabelFrame(
            self.input_options, text="Sizes", bg=self.gl.background_color, width=130, height=105, bd=2)
        size_labelframe.place(x=5, y=0)

        self.padlock_button = tkinter.Button(
            size_labelframe, bg=self.gl.background_color,
            relief=RAISED, image=self.gl.padlock_unlock_image, command=self.padlock)
        self.padlock_button.place(x=85, y=30)

        balloon_padlock = Pmw.Balloon(self.root)
        balloon_padlock.bind(self.padlock_button, "Lock width & height")

        # vcmd = (size_labelframe.register(validate_data), '%P')
        # vcmd = (size_labelframe.register(self.padlock), '%P')

        def width_focus(event):
            width_id = self.width_entry.winfo_id()
            # height_id = self.height_entry.winfo_id()
            if event.widget.winfo_id() == width_id:
                # locked
                if self.padlock_button.cget('image') == 'pyimage3':
                    try:
                        w = self.gl.width_entry_variable.get()
                        self.height_entry.delete(0, tkinter.END)
                        self.height_entry.insert(0, w)
                    except:
                        return

        def height_focus(event):
            # width_id = self.width_entry.winfo_id()
            height_id = self.height_entry.winfo_id()
            if event.widget.winfo_id() == height_id:
                # locked
                if self.padlock_button.cget('image') == 'pyimage3':
                    try:
                        h = self.gl.height_entry_variable.get()
                        self.width_entry.delete(0, tkinter.END)
                        self.width_entry.insert(0, h)
                    except:
                        return

        tkinter.Label(size_labelframe, text="width", bg=self.gl.background_color).place(x=5, y=10)
        self.width_entry = tkinter.Entry(size_labelframe, width=4, bd=2, textvariable=self.gl.width_entry_variable)
        # validate="key", validatecommand=vcmd)
        self.width_entry.place(x=50, y=10)
        self.width_entry.bind('<FocusOut>', lambda event: width_focus(event))
        balloon_width = Pmw.Balloon(self.root)
        balloon_width.bind(self.width_entry, "Sub sprite width")

        tkinter.Label(size_labelframe, text="height", bg=self.gl.background_color).place(x=5, y=50)
        self.height_entry = tkinter.Entry(size_labelframe, width=4, bd=2,  textvariable=self.gl.height_entry_variable)
        # validate="key", validatecommand=vcmd, )
        self.height_entry.place(x=50, y=50)
        self.height_entry.bind('<FocusOut>', lambda event: height_focus(event))
        balloon_height = Pmw.Balloon(self.root)
        balloon_height.bind(self.height_entry, "Sub sprite height")

        rowsxcolumns_labelframe = tkinter.LabelFrame(
            self.input_options, text="Rows & columns", bg=self.gl.background_color, width=120, height=105, bd=2)
        rowsxcolumns_labelframe.place(x=140, y=0)

        tkinter.Label(rowsxcolumns_labelframe, text="Rows:", bg=self.gl.background_color).place(x=5, y=10)
        tkinter.Entry(rowsxcolumns_labelframe, width=2, bd=2, textvariable=self.gl.rows_value).place(x=45, y=10)
        tkinter.Label(rowsxcolumns_labelframe, text="Cols:", bg=self.gl.background_color).place(x=5, y=50)
        tkinter.Entry(rowsxcolumns_labelframe, width=2, bd=2, textvariable=self.gl.columns_value).place(x=45, y=50)

        input_file_format = tkinter.LabelFrame(
            self.input_options, text="Image format", bg=self.gl.background_color, width=85, height=105, bd=2)
        input_file_format.place(x=265, y=0)

        self.format_24bit = tkinter.Checkbutton(
            input_file_format, text='24-bit', bg=self.gl.background_color, variable=self.gl.input_format_24bit,
            onvalue=1, offvalue=0, command=self.tickbox_24bit)
        self.format_24bit.place(x=5, y=10)
        balloon_format24 = Pmw.Balloon(self.root)
        balloon_format24.bind(self.format_24bit,
                              "Tick the box if your spritesheet image format is 24-bit\n"
                              "Image format 24-bit does not contains the alpha channel\n"
                              " for transparency.Your spritesheet background pixel is most\n"
                              " to be a solid colour e.g black or white")

        self.format_32bit = tkinter.Checkbutton(
            input_file_format, text='32-bit', bg=self.gl.background_color, variable=self.gl.input_format_32bit,
            onvalue=1, offvalue=0, command=self.tickbox_32bit)
        self.format_32bit.place(x=5, y=50)
        balloon_format32 = Pmw.Balloon(self.root)
        balloon_format32.bind(self.format_32bit,
                              "Tick the box if your spritesheet image format is 32-bit\n"
                              "Image format 32-bit contains the alpha channel for transparency\n"
                              )

        # transparency_labelframe = LabelFrame(
        #     self.input_options, text="Transparency", bg=self.gl.bkcolor, width=195, height=105, bd=2)
        # transparency_labelframe.place(x=275, y=0)
        #
        # self.input_rleaccel = Checkbutton(
        #     transparency_labelframe, text='RLEACCEL', bg=self.gl.bkcolor, variable=self.gl.rleaccel_value,
        #     onvalue=1, offvalue=0, command=dummy)
        # self.input_rleaccel.place(x=5, y=0)
        # balloon_output_rleaccel = Pmw.Balloon(self.root)
        # balloon_output_rleaccel.bind(self.input_rleaccel, "Add RLE acceleration.\n"
        #                              "Only compatible for 24-bit format.")
        #
        # self.input_setalpha = Checkbutton(
        #     transparency_labelframe, text='Set alpha', bg=self.gl.bkcolor, variable=self.gl.set_alpha_value,
        #     onvalue=1, offvalue=0, command=dummy)
        # self.input_setalpha.place(x=5, y=30)
        # balloon_output_setalpha = Pmw.Balloon(self.root)
        # balloon_output_setalpha.bind(self.input_setalpha, "Set alpha transparency.")
        #
        # self.input_colorkey = Checkbutton(
        #     transparency_labelframe, text='Colorkey', bg=self.gl.bkcolor, variable=self.gl.colorkey,
        #     onvalue=1, offvalue=0, command=dummy)
        # self.input_colorkey.place(x=5, y=60)
        # balloon_output_colorkey = Pmw.Balloon(self.root)
        # balloon_output_colorkey.bind(self.input_colorkey, "Set the colorkey.")
        #
        # self.input_colorkey_edit = Button(
        #     transparency_labelframe,
        #     text="Edit colors",
        #     image=self.gl.color_icon,
        #     command=lambda: select_color(self.gl.colorkey_red, self.gl.colorkey_green, self.gl.colorkey_blue)
        #     )
        # self.input_colorkey_edit.place(x=85, y=35)
        # balloon_output_colorkey_edit = Pmw.Balloon(self.root)
        # balloon_output_colorkey_edit.bind(self.input_colorkey_edit, "Choose the colorkey.")
        #
        # Label(transparency_labelframe, text="Red", bg=self.gl.bkcolor).place(x=115, y=5)
        # Label(transparency_labelframe, text="Green", bg=self.gl.bkcolor).place(x=115, y=35)
        # Label(transparency_labelframe, text="Blue", bg=self.gl.bkcolor).place(x=115, y=65)
        # self.input_red = Entry(transparency_labelframe, validate="key", width=3, bd=2,
        #                        textvariable=self.gl.colorkey_red)
        # self.input_red.place(x=160, y=0)
        # self.input_green = Entry(transparency_labelframe, validate="key", width=3, bd=2,
        #                          textvariable=self.gl.colorkey_green)
        # self.input_green.place(x=160, y=30)
        # self.input_blue = Entry(transparency_labelframe, validate="key", width=3, bd=2,
        #                         textvariable=self.gl.colorkey_blue)
        # self.input_blue.place(x=160, y=60)

        loading_button = tkinter.Button(
            self.input_options, text="Load", width=20, height=1, bg=self.gl.background_color,
            command=self.open_spritesheet)
        loading_button.place(x=10, y=115)
        balloon_loading_button = Pmw.Balloon(self.root)
        balloon_loading_button.bind(loading_button,
                                    "Load your spritesheet (you should be able to load most\n"
                                    "images (including PNG, JPG and GIF). Prior loading the\n"
                                    "spritesheet, select the image format (24-bit or 32-bit).\n"
                                    "Spritesheet format 8-bit are not compatible with this\n "
                                    "version of SpriteStudio")

        tkinter.Label(self.input_options, text="filename", bg="#858585").place(x=170, y=120)

        spritesheet_name = tkinter.Entry(
            self.input_options, width=35, bd=2, state=DISABLED, textvariable=self.gl.spritesheet_name_variable)
        spritesheet_name.place(x=230, y=120)

    def output_options(self):
        self.output_option = LabelFrame(
            self.root, text="OUTPUT options", bg=self.gl.bkcolor, width=475, height=170, bd=2)
        self.output_option.place(x=5, y=175)

        rescale_labelframe = LabelFrame(
            self.output_option, text="Rescale", bg=self.gl.bkcolor, width=240, height=130, bd=2)
        rescale_labelframe.place(x=5, y=5)

        Label(rescale_labelframe, text="width:", bg=self.gl.bkcolor).place(x=5, y=10)
        Label(rescale_labelframe, text="height:", bg=self.gl.bkcolor).place(x=5, y=50)
        self.output_width = Entry(rescale_labelframe, width=4, bd=2, textvariable=self.gl.output_width_value)
        self.output_width.place(x=50, y=10)
        self.output_height = Entry(rescale_labelframe, width=4, bd=2, textvariable=self.gl.output_height_value)
        self.output_height.place(x=50, y=50)

        Label(rescale_labelframe, text="rows:", bg=self.gl.bkcolor).place(x=85, y=10)
        Label(rescale_labelframe, text="columns:", bg=self.gl.bkcolor).place(x=85, y=50)
        Entry(rescale_labelframe, width=3, bd=2, textvariable=self.gl.output_rows_value).place(x=140, y=10)
        Entry(rescale_labelframe, width=3, bd=2, textvariable=self.gl.output_columns_value).place(x=140, y=50)

        balloon_output_width = Pmw.Balloon(self.root)
        balloon_output_width.bind(self.output_width, "Output sprite's width")
        balloon_output_height = Pmw.Balloon(self.root)
        balloon_output_height.bind(self.output_height, "Output sprite's height")

        format_labelframe = LabelFrame(
            self.output_option, text="Image format", bg=self.gl.bkcolor, width=100, height=130, bd=2)
        format_labelframe.place(x=250, y=5)

        output_format24 = Checkbutton(
            format_labelframe, text='24-bit', bg=self.gl.bkcolor,
            variable=self.gl.output_format_24bit, onvalue=1, offvalue=0, command=dummy)
        output_format24.place(x=10, y=10)
        balloon_output_format24 = Pmw.Balloon(self.root)
        balloon_output_format24.bind(output_format24, "Convert your spritesheet for a fast blit.\n"
                                                      "alpha channel will be removed")

        output_format32 = Checkbutton(
            format_labelframe, text='32-bit', bg=self.gl.bkcolor, variable=self.gl.output_format_32bit,
            onvalue=1, offvalue=0, command=dummy)
        output_format32.place(x=10, y=50)
        balloon_output_format32 = Pmw.Balloon(self.root)
        balloon_output_format32.bind(output_format32, "Convert your spritesheet to a 32-bit format.\n"
                                                      "Keep alpha channel of the original spritesheet.")

        """
        pygame.image.save()
        save an image to file (or file-like object)
        save(Surface, filename) -> None
        save(Surface, fileobj, namehint="") -> None
        This will save your Surface as either a BMP, TGA, PNG, or JPEG image. 
        If the filename extension is unrecognized it will default to TGA. Both
        TGA, and BMP file formats create uncompressed files. You can pass a 
        filename or a Python file-like object. For file-like object, the image is
        saved to TGA format unless a namehint with a recognizable extension is passed in.
        
        Note To be able to save the JPEG file format to a file-like object, 
        SDL2_Image version 2.0.2 or newer is needed.
        Note When saving to a file-like object, it seems that for most formats, 
        the object needs to be flushed after saving to it to make loading from it possible.
        Changed in pygame 1.8: Saving PNG and JPEG files.
        
        Changed in pygame 2.0.0.dev11: The namehint parameter was added to make it possible 
        to save other formats than TGA to a file-like object.
        
        JPG
        PNG
        GIF (non-animated)
        BMP
        PCX
        TGA (uncompressed)
        TIF
        LBM (and PBM)
        PBM (and PGM, PPM)
        XPM
        Saving images only supports a limited set of formats. You can save to the following formats.
        
        BMP
        TGA
        PNG
        JPEG
        """

        self.output_file_format = ttk.Combobox(
            self.output_option, text='format', textvariable=self.gl.file_format_value, state='readonly', width=10)
        output_file_combo_ballon = Pmw.Balloon(self.root)
        output_file_combo_ballon.bind(self.output_file_format, "Choose a file format")
        self.output_file_format.place(x=55, y=105)
        self.output_file_format.config(values=["PNG", "JPEG", "TGA", "BMP"])
        self.output_file_format.current(0)

        # transparency_labelframe = LabelFrame(
        #     self.output_option, text="Transparency", bg=self.gl.bkcolor, width=230, height=130, bd=2)
        # transparency_labelframe.place(x=235, y=5)
        #
        # output_rleaccel = Checkbutton(
        #     transparency_labelframe, text='RLEACCEL', bg=self.gl.bkcolor, variable=self.gl.rleaccel_value,
        #     onvalue=1, offvalue=0, command=dummy)
        # output_rleaccel.place(x=10, y=10)
        # balloon_output_rleaccel = Pmw.Balloon(self.root)
        # balloon_output_rleaccel.bind(output_rleaccel, "Add RLE acceleration.\n"
        #                                               "Only compatible for 24-bit format.")
        #
        # output_setalpha = Checkbutton(
        #     transparency_labelframe, text='Set alpha', bg=self.gl.bkcolor, variable=self.gl.set_alpha_value,
        #     onvalue=1, offvalue=0, command=dummy)
        # output_setalpha.place(x=10, y=40)
        # balloon_output_setalpha = Pmw.Balloon(self.root)
        # balloon_output_setalpha.bind(output_setalpha, "Set alpha transparency.")
        #
        # output_colorkey = Checkbutton(
        #     transparency_labelframe, text='Colorkey', bg=self.gl.bkcolor, variable=self.gl.colorkey,
        #     onvalue=1, offvalue=0, command=dummy)
        # output_colorkey.place(x=10, y=70)
        # balloon_output_colorkey = Pmw.Balloon(self.root)
        # balloon_output_colorkey.bind(output_colorkey, "Set the colorkey.")
        #
        # output_colorkey_edit = Button(
        #     transparency_labelframe,
        #     text="Edit colors",
        #     image=self.gl.color_icon,
        #     command=lambda: select_color(self.gl.colorkey_red, self.gl.colorkey_green, self.gl.colorkey_blue)
        #     )
        # output_colorkey_edit.place(x=110, y=40)
        # balloon_output_colorkey_edit = Pmw.Balloon(self.root)
        # balloon_output_colorkey_edit.bind(output_colorkey_edit, "Choose the colorkey.")
        #
        # Label(transparency_labelframe, text="Red", bg=self.gl.bkcolor).place(x=140, y=15)
        # Label(transparency_labelframe, text="Green", bg=self.gl.bkcolor).place(x=140, y=45)
        # Label(transparency_labelframe, text="Blue", bg=self.gl.bkcolor).place(x=140, y=75)
        # Entry(transparency_labelframe, validate="key", width=4, bd=2,
        #       textvariable=self.gl.colorkey_red).place(x=180, y=15)
        # Entry(transparency_labelframe, validate="key", width=4, bd=2,
        #       textvariable=self.gl.colorkey_green).place(x=180, y=45)
        # Entry(transparency_labelframe, validate="key", width=4, bd=2,
        #       textvariable=self.gl.colorkey_blue).place(x=180, y=75)

    def blending_effect(self):

        self.empty = LabelFrame(self.root, text='EFFECTS', bg="#858585", width=475, height=290, bd=2)
        self.empty.place(x=5, y=345)

        blending_effect = LabelFrame(self.empty, text="Blending", bg=self.gl.bkcolor, width=470, height=130, bd=2)
        blending_effect.place(x=0, y=5)

        self.blend_checkbox = tkinter.BooleanVar()
        self.blend_checkbox.set(False)
        blend_checkbutton = Checkbutton(
            blending_effect, text='Blend', bg=self.gl.bkcolor,
            variable=self.blend_checkbox, onvalue=1, offvalue=0, command=dummy)
        blend_checkbutton.place(x=10, y=40)

        blend_checkbutton_balloon = Pmw.Balloon(self.root)
        blend_checkbutton_balloon.bind(blend_checkbutton, "Create a blend effect")

        Label(blending_effect, text="Blend with", bg=self.gl.bkcolor).place(x=90, y=0)
        Label(blending_effect, text="Red", bg=self.gl.bkcolor).place(x=70, y=20)
        Label(blending_effect, text="Green", bg=self.gl.bkcolor).place(x=70, y=50)
        Label(blending_effect, text="Blue", bg=self.gl.bkcolor).place(x=70, y=80)
        Entry(blending_effect, validate="key", width=4, bd=2, textvariable=self.gl.red).place(x=110, y=20)
        Entry(blending_effect, validate="key", width=4, bd=2, textvariable=self.gl.green).place(x=110, y=50)
        Entry(blending_effect, validate="key", width=4, bd=2, textvariable=self.gl.blue).place(x=110, y=80)

        edit_color_button = Button(
            blending_effect, text="Edit colors", image=self.gl.color_icon,
            command=lambda: select_color(self.gl.red, self.gl.green, self.gl.blue))
        edit_color_button.place(x=150, y=50)
        color_balloon = Pmw.Balloon(self.root)
        color_balloon.bind(edit_color_button, "Choose a specific color to blend with the sprite image")

        Label(blending_effect, text="Exclude", bg=self.gl.bkcolor).place(x=195, y=0)
        Label(blending_effect, text="Red", bg=self.gl.bkcolor).place(x=180, y=20)
        Label(blending_effect, text="Green", bg=self.gl.bkcolor).place(x=180, y=50)
        Label(blending_effect, text="Blue", bg=self.gl.bkcolor).place(x=180, y=80)
        self.exclude_red_entry = Entry(
            blending_effect, validate="key", width=4, bd=2, textvariable=self.gl.exclude_red)
        self.exclude_red_entry.place(x=220, y=20)
        self.exclude_green_entry = Entry(
            blending_effect, validate="key", width=4, bd=2, textvariable=self.gl.exclude_green)
        self.exclude_green_entry.place(x=220, y=50)
        self.exclude_blue_entry = Entry(
            blending_effect, validate="key", width=4, bd=2, textvariable=self.gl.exclude_blue)
        self.exclude_blue_entry.place(x=220, y=80)

        self.exclude_button = Button(
            blending_effect, text="Edit colors", image=self.gl.color_icon,
            command=lambda: select_color(self.gl.exclude_red, self.gl.exclude_green, self.gl.exclude_blue))
        self.exclude_button.place(x=260, y=50)
        exclude_balloon = Pmw.Balloon(self.root)
        exclude_balloon.bind(self.exclude_button, "Choose a specific color to be ignored\n"
                                                  " during the blending process (example\n"
                                                  " black color background for a 24-bit\n"
                                                  " sprite image.")

        Label(blending_effect, text="Start frame", bg=self.gl.bkcolor).place(x=270, y=10)
        Entry(blending_effect, validate="key", width=4, bd=2, textvariable=self.gl.blend_start_frame).place(x=340, y=10)

        Label(blending_effect, text="End frame", bg=self.gl.bkcolor).place(x=370, y=10)
        Entry(blending_effect, validate="key", width=4, bd=2, textvariable=self.gl.blend_end_frame).place(x=435, y=10)

        Label(blending_effect, text="Percentage", bg=self.gl.bkcolor).place(x=310, y=40)
        Label(blending_effect, text="0", bg=self.gl.bkcolor).place(x=300, y=80)
        Label(blending_effect, text="100%", bg=self.gl.bkcolor).place(x=415, y=80)

        scale = Scale(blending_effect, bg=self.gl.bkcolor, orient=HORIZONTAL, bd=2, relief=FLAT,
                      activebackground=self.gl.bkcolor, troughcolor="LIGHTGRAY", highlightbackground=self.gl.bkcolor,
                      variable=self.gl.blend_scale_percentage, from_=0.0, to_=100.0, width=10)
        scale.place(x=310, y=60)
        scale_balloon = Pmw.Balloon(self.root)
        scale_balloon.bind(scale, "Adjust the blend value [0 ... 100%]")

    def hsv_preview_update(self, hsv_scale_value):

        if not (isinstance(self.gl.pyimage, list) and len(self.gl.pyimage) != 0):
            return

        pyimage = self.gl.pyimage[0]
        v = int(hsv_scale_value)
        h = float((v + 180) / 360.0)
        if self.gl.input_format_24bit.get():
            pyimage = hsv_surface24c(pyimage, h)
            pyimage = pygame.transform.smoothscale(pyimage, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.hsv_preview.image = tkinter_image
            self.hsv_preview.config(image=tkinter_image)
            self.hsv_preview.update()

        else:
            pyimage = hsv_surface32c(pyimage, h)
            pyimage = pygame.transform.smoothscale(pyimage, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.hsv_preview.image = tkinter_image
            self.hsv_preview.config(image=tkinter_image)
            self.hsv_preview.update()

    def hsv_effect(self):

        hsv_effect = LabelFrame(self.empty, text="Hsv", bg=self.gl.bkcolor, width=470, height=110, bd=2)
        hsv_effect.place(x=0, y=145)

        hsv_checkbutton = Checkbutton(
            hsv_effect, text='hsv', bg=self.gl.bkcolor, variable=self.gl.hsv_checkbox,
            onvalue=1, offvalue=0, command=dummy)
        hsv_checkbutton.place(x=10, y=5)

        hsv_checkbutton_ballon = Pmw.Balloon(self.root)
        hsv_checkbutton_ballon.bind(hsv_checkbutton, "Create a hue rotation effect")

        Label(hsv_effect, text="-180", bg=self.gl.bkcolor).place(x=5, y=50)
        Label(hsv_effect, text="+180", bg=self.gl.bkcolor).place(x=210, y=50)

        hsv_rotate = Checkbutton(
            hsv_effect, text='hsv rotate', bg=self.gl.bkcolor, variable=self.gl.hsv_rotate, onvalue=1,
            offvalue=0, command=dummy)
        hsv_rotate.place(x=60, y=5)
        hsv_rotate_ballon = Pmw.Balloon(self.root)
        hsv_rotate_ballon.bind(hsv_rotate, "Rotate the hue from -180 to +180")

        xx = 150
        yy = 7
        Label(hsv_effect, text="Start frame", bg=self.gl.bkcolor).place(x=xx, y=yy)
        Entry(hsv_effect, width=4, bd=2, textvariable=self.gl.hsvstart_frame).place(x=xx + 70, y=yy)

        Label(hsv_effect, text="End frame", bg=self.gl.bkcolor).place(x=xx + 100, y=yy)
        Entry(hsv_effect, validate="key", width=4, bd=2, textvariable=self.gl.hsvend_frame).place(x=xx + 165, y=yy)

        self.hsv_preview = Label(hsv_effect, bg=self.gl.bkcolor, relief=RAISED, image=self.gl.preview_image)
        self.hsv_preview.place(x=360, y=10)

        scale = Scale(hsv_effect, bg=self.gl.bkcolor, orient=HORIZONTAL, bd=2, relief=FLAT,
                      activebackground=self.gl.bkcolor, troughcolor="LIGHTGRAY", variable=self.gl.hsv_scale_value,
                      length=180, highlightbackground=self.gl.bkcolor, from_=-180, to_=180,
                      width=10, command=self.hsv_preview_update)

        scale.place(x=35, y=30)
        scale_balloon = Pmw.Balloon(self.root)
        scale_balloon.bind(scale, "Adjust the hue value. This value will be ignore if hsv rotate is ticked.")

    def bloom_preview_update(self, highpass_filter_value_):

        if not (isinstance(self.gl.pyimage, list) and len(self.gl.pyimage) != 0):
            return

        pyimage = gl.pyimage[0]
        v = int(highpass_filter_value_)
        if gl.input_format_24bit.get():

            pyimage = bloom_effect_array24(pyimage.convert(24), v, 1)
            pyimage = pygame.transform.smoothscale(pyimage, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.bloom_preview.image = tkinter_image
            self.bloom_preview.config(image=tkinter_image)
            self.bloom_preview.update()

        else:
            pyimage = bloom_effect_array32(pyimage, v, 1)
            pyimage = pygame.transform.smoothscale(pyimage, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.bloom_preview.image = tkinter_image
            self.bloom_preview.config(image=tkinter_image)
            self.bloom_preview.update()

    def bloom_effect(self):

        bloom_effect = LabelFrame(self.effect_labelframe, text="Bloom", bg=self.gl.bkcolor, width=475, height=110, bd=2)
        bloom_effect.place(x=0, y=5)

        bloom_checkbutton = Checkbutton(
            bloom_effect, text='Bloom', bg=self.gl.bkcolor,
            variable=self.gl.bloom_checkbox, onvalue=1, offvalue=0, command=dummy)
        bloom_checkbutton.place(x=10, y=25)
        bloom_ballon = Pmw.Balloon(self.root)
        bloom_ballon.bind(bloom_checkbutton, "Create a bloom effect")

        xx = 150
        yy = 7
        Label(bloom_effect, text="Start frame", bg=self.gl.bkcolor).place(x=xx, y=yy)
        Entry(bloom_effect, validate="key", width=4, bd=2, textvariable=self.gl.bloomstart_frame).place(x=xx + 70, y=yy)
        Label(bloom_effect, text="End frame", bg=self.gl.bkcolor).place(x=xx + 100, y=yy)
        Entry(bloom_effect, validate="key", width=4, bd=2, textvariable=self.gl.bloomend_frame).place(x=xx + 165, y=yy)
        self.bloom_preview = Label(bloom_effect, bg=self.gl.bkcolor, relief=RAISED, image=self.gl.preview_image)
        self.bloom_preview.place(x=360, y=10)

        bloom_scale = Scale(
            bloom_effect, bg=self.gl.bkcolor, orient=HORIZONTAL, bd=2, relief=FLAT,
            activebackground=self.gl.bkcolor, troughcolor="LIGHTGRAY", variable=self.gl.highpass_filter_value,
            length=255, highlightbackground=self.gl.bkcolor, from_=0, to_=255, label="Bright pass filter",
            width=10, command=self.bloom_preview_update)
        bloom_scale.place(x=80, y=25)
        bloom_scale_ballon = Pmw.Balloon(self.root)
        bloom_scale_ballon.bind(bloom_scale, "Adjust the high pass filter level (0 maximum bloom)")

    def saturation_preview_update(self, saturation_sacle_value_):

        if not (isinstance(self.gl.pyimage, list) and len(self.gl.pyimage) != 0):
            return

        pyimage = self.gl.pyimage[0]
        v = float(saturation_sacle_value_)

        if self.gl.input_format_24bit.get():

            rgb_array = pygame.surfarray.array3d(pyimage)
            pyimage = saturation_array24(rgb_array, v, swap_row_column=False)
            pyimage = pygame.transform.smoothscale(pyimage, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.saturation_preview.image = tkinter_image
            self.saturation_preview.config(image=tkinter_image)
            self.saturation_preview.update()

        else:

            rgb_array = pygame.surfarray.array3d(pyimage)
            alpha_array = pygame.surfarray.array_alpha(pyimage)
            pyimage = saturation_array32(rgb_array, alpha_array, v, swap_row_column=False)
            pyimage = pygame.transform.smoothscale(pyimage, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.saturation_preview.image = tkinter_image
            self.saturation_preview.config(image=tkinter_image)
            self.saturation_preview.update()

    def saturation_effect(self):

        saturation_effect_labelframe = LabelFrame(
            self.effect_labelframe, text="Saturation", bg=self.gl.bkcolor, width=475, height=110, bd=2)
        saturation_effect_labelframe.place(x=0, y=125)

        sat_checkbutton = Checkbutton(
            saturation_effect_labelframe, text='Saturation', bg=self.gl.bkcolor,
            variable=self.gl.saturation_checkbox,
            onvalue=1, offvalue=0, command=dummy)
        sat_checkbutton.place(x=5, y=30)
        sat_ballon = Pmw.Balloon(self.root)
        sat_ballon.bind(sat_checkbutton, "Create a saturation effect")

        scale = Scale(
            saturation_effect_labelframe, bg=self.gl.bkcolor, orient=HORIZONTAL, bd=2, relief=FLAT,
            font=tkFont.Font(family='Helvetica', size=8, weight='normal'), activebackground=self.gl.bkcolor,
            troughcolor="LIGHTGRAY", variable=self.gl.saturation_scale_value, length=255,
            highlightbackground=self.gl.bkcolor,
            from_=-1.00, to_=1.00, tickinterval=1, resolution=0.1, digits=2, label="Saturation level", width=10,
            command=self.saturation_preview_update)
        scale.place(x=90, y=5)
        scale_ballon = Pmw.Balloon(self.root)
        scale_ballon.bind(scale, "Saturation level range [-1.0 ... +1.0]")

        self.saturation_preview = Label(
            saturation_effect_labelframe, bg=self.gl.bkcolor, relief=RAISED, image=self.gl.preview_image)
        self.saturation_preview.place(x=360, y=10)

    def cartoon_effect(self):

        cartoons_effect_labelframe = LabelFrame(
            self.effect_labelframe, text="Cartoonish", bg=self.gl.bkcolor, width=475, height=110, bd=2)
        cartoons_effect_labelframe.place(x=0, y=245)

        cartoon_checkbutton = Checkbutton(
            cartoons_effect_labelframe, text='Cartoon', bg=self.gl.bkcolor,
            variable=self.gl.cartoon_checkbox, onvalue=1,
            offvalue=0, command=dummy)
        cartoon_checkbutton.place(x=5, y=30)
        cartoon_checkbutton_balloon = Pmw.Balloon(self.root)
        cartoon_checkbutton_balloon.bind(cartoon_checkbutton, "Create a cartoon effect")

        def greyscale_lightness():
            light = self.gl.cartoon_lightness.get()
            if light:
                self.gl.cartoon_luminosity.set(0)
                self.gl.cartoon_average.set(0)
            self.gl.cartoon_lightness.set(1)

            cartoon_lightness.update()
            cartoon_luminosity.update()
            cartoon_average.update()

        def greyscale_luminosity():
            light = self.gl.cartoon_luminosity.get()
            if light:
                self.gl.cartoon_lightness.set(0)
                self.gl.cartoon_average.set(0)
            self.gl.cartoon_luminosity.set(1)

            cartoon_lightness.update()
            cartoon_luminosity.update()
            cartoon_average.update()

        def greyscale_average():
            light = self.gl.cartoon_average.get()
            if light:
                self.gl.cartoon_lightness.set(0)
                self.gl.cartoon_luminosity.set(0)
            self.gl.cartoon_average.set(1)

            cartoon_lightness.update()
            cartoon_luminosity.update()
            cartoon_average.update()

        cartoon_lightness = Checkbutton(
            cartoons_effect_labelframe, text='lightness', bg=self.gl.bkcolor,
            variable=self.gl.cartoon_lightness, onvalue=1, offvalue=0, command=greyscale_lightness)
        cartoon_lightness.place(x=75, y=5)
        balloon_lightness = Pmw.Balloon(self.root)
        balloon_lightness.bind(cartoon_lightness, "grayscale conserve lightness")

        cartoon_luminosity = Checkbutton(
            cartoons_effect_labelframe, text='luminosity', bg=self.gl.bkcolor,
            variable=self.gl.cartoon_luminosity, onvalue=1, offvalue=0, command=greyscale_luminosity)
        cartoon_luminosity.place(x=75, y=30)
        balloon_lumi = Pmw.Balloon(self.root)
        balloon_lumi.bind(cartoon_luminosity, "grayscale conserve luminosity")

        cartoon_average = Checkbutton(
            cartoons_effect_labelframe, text='average', bg=self.gl.bkcolor,
            variable=self.gl.cartoon_average, onvalue=1, offvalue=0, command=greyscale_average)
        cartoon_average.place(x=75, y=55)
        balloon_avg = Pmw.Balloon(self.root)
        balloon_avg.bind(cartoon_average, "grayscale average")

        cartoons_edge_labelframe = LabelFrame(
            cartoons_effect_labelframe, text="edge detection", bg=self.gl.bkcolor, width=100, height=80, bd=2)
        cartoons_edge_labelframe.place(x=160, y=0)
        Label(cartoons_edge_labelframe, text="Tresh", bg="#858585").place(x=5, y=15)
        treshold = Entry(cartoons_edge_labelframe, width=3, textvariable=self.gl.cartoon_threshold)
        treshold.place(x=40, y=15)
        balloon_threshold = Pmw.Balloon(self.root)
        balloon_threshold.bind(treshold, "Canny edge detection threshold, default\n"
                                         "value is 20. Below 20 increase number of edges\n"
                                         "and above 20 decrease overall detection\n"
                                         "Value must be in range [0 ... 100] default is 20.")

        cartoons_median_labelframe = LabelFrame(
            cartoons_effect_labelframe, text="median filter", bg=self.gl.bkcolor, width=100, height=80, bd=2)
        cartoons_median_labelframe.place(x=265, y=0)
        Label(cartoons_median_labelframe, text="size ", bg="#858585").place(x=5, y=15)
        size = Entry(cartoons_median_labelframe, width=3, textvariable=self.gl.cartoon_neightboors)
        size.place(x=40, y=15)

        balloon_size = Pmw.Balloon(self.root)
        balloon_size.bind(size, " Size of neighborhood pixels\n"
                                " The median is calculated by first sorting all\n"
                                " the pixel values from the surrounding neighborhood\n"
                                " into numerical order and then replacing the pixel\n"
                                " being considered with the middle pixel value.\n "
                                "neighborhood must be in range [1 ... 16]\n"
                                "default is 4. Median filter will be disregarded if value is zero")

        cartoons_reduction_labelframe = LabelFrame(
            cartoons_effect_labelframe, text="color reduction", bg=self.gl.bkcolor, width=100, height=80, bd=2)
        cartoons_reduction_labelframe.place(x=370, y=0)
        Label(cartoons_reduction_labelframe, text="bits ", bg="#858585").place(x=5, y=15)
        color = Entry(cartoons_reduction_labelframe, width=3, textvariable=self.gl.cartoon_color)
        color.place(x=40, y=15)
        balloon_color = Pmw.Balloon(self.root)
        balloon_color.bind(color, " Image depth, default 16-bits.\n"
                                  "Value must be in range [0 ... 65535]\n"
                                  "Color reduction will be disregarded if\n"
                                  "value is zero.")

    def blur_effect_preview_update(self):

        if not (isinstance(self.gl.pyimage, list) and len(self.gl.pyimage) != 0):
            return

        pyimage = self.gl.pyimage[0]

        blurx2 = self.gl.blurx2.get()
        blurx4 = self.gl.blurx4.get()
        blurx6 = self.gl.blurx6.get()

        passes = 1
        if blurx2:
            passes = 2
        if blurx4:
            passes = 4
        if blurx6:
            passes = 6

        if self.gl.input_format_24bit.get():
            for _ in range(passes):
                rgb_array = pygame.surfarray.array3d(pyimage)
                pyimage = pygame.surfarray.make_surface(numpy.asarray(blur5x5_array24(rgb_array)))

            pyimage = pygame.transform.smoothscale(pyimage, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.blur_preview.image = tkinter_image
            self.blur_preview.config(image=tkinter_image)
            self.blur_preview.update()

        else:
            for _ in range(passes):
                rgb_array = pygame.surfarray.array3d(pyimage)
                alpha_array = pygame.surfarray.array_alpha(pyimage)
                rgba_array = numpy.dstack((rgb_array, alpha_array)).transpose(1, 0, 2)
                w, h = rgba_array.shape[:2]
                pyimage = pygame.image.frombuffer(blur5x5_array32(rgba_array), (w, h), 'RGBA')
            pyimage = pygame.transform.smoothscale(pyimage, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.blur_preview.image = tkinter_image
            self.blur_preview.config(image=tkinter_image)
            self.blur_preview.update()

    def blurx2(self):
        if self.gl.blurx2.get():
            self.gl.blurx4.set(0)
            self.gl.blurx6.set(0)
        self.blur_effect_preview_update()

    def blurx4(self):
        if self.gl.blurx4.get():
            self.gl.blurx2.set(0)
            self.gl.blurx6.set(0)
        self.blur_effect_preview_update()

    def blurx6(self):
        if self.gl.blurx6.get():
            self.gl.blurx2.set(0)
            self.gl.blurx4.set(0)
        self.blur_effect_preview_update()

    def blur_effect(self):

        blur_effect_labelrame = LabelFrame(
            self.effect_labelframe, text="Blur",
            bg=self.gl.bkcolor, width=475, height=110, bd=2)
        blur_effect_labelrame.place(x=0, y=365)

        blur_checkbutton = Checkbutton(
            blur_effect_labelrame, text='Blur', bg=self.gl.bkcolor, variable=self.gl.blur_checkbox,
            onvalue=1, offvalue=0, command=dummy)
        blur_checkbutton.place(x=10, y=5)
        blur_checkbutton_balloon = Pmw.Balloon(self.root)
        blur_checkbutton_balloon.bind(blur_checkbutton, "Apply a gaussian blur kernel 5x5 ")

        progressive_blur = Checkbutton(
            blur_effect_labelrame, text='progressive', bg=self.gl.bkcolor, variable=self.gl.blur_progressive,
            onvalue=1, offvalue=0, command=dummy)
        progressive_blur.place(x=60, y=5)
        progressive_blur_ballon = Pmw.Balloon(self.root)
        progressive_blur_ballon.bind(progressive_blur, "Apply a progressive blur effect")

        xx = 10
        yy = 40

        blurx2 = Checkbutton(
            blur_effect_labelrame, text='x2', bg=self.gl.bkcolor, variable=self.gl.blurx2,
            onvalue=1, offvalue=0, command=self.blurx2)
        blurx2.place(x=xx, y=yy)
        blurx2_ballon = Pmw.Balloon(self.root)
        blurx2_ballon.bind(blurx2, "Apply gaussian blur effect kernel 5x5 times x2")

        blurx4 = Checkbutton(
            blur_effect_labelrame, text='x4', bg=self.gl.bkcolor, variable=self.gl.blurx4,
            onvalue=1, offvalue=0, command=self.blurx4)
        blurx4.place(x=xx + 50, y=yy)
        blurx4_ballon = Pmw.Balloon(self.root)
        blurx4_ballon.bind(blurx4, "Apply gaussian blur effect kernel 5x5 times x4")

        blurx6 = Checkbutton(
            blur_effect_labelrame, text='x6', bg=self.gl.bkcolor, variable=self.gl.blurx6,
            onvalue=1, offvalue=0, command=self.blurx6)
        blurx6.place(x=xx + 100, y=yy)
        blurx6_ballon = Pmw.Balloon(self.root)
        blurx6_ballon.bind(blurx6, "Apply gaussian blur effect kernel 5x5 times x6")

        xx = 150
        yy = 7
        Label(blur_effect_labelrame, text="Start frame", bg=self.gl.bkcolor).place(x=xx, y=yy)
        Entry(blur_effect_labelrame, validate="key", width=4, bd=2,
              textvariable=self.gl.blurstart_frame).place(x=xx + 70, y=yy)
        Label(blur_effect_labelrame, text="End frame", bg=self.gl.bkcolor).place(x=xx + 100, y=yy)
        Entry(blur_effect_labelrame, validate="key", width=4, bd=2,
              textvariable=self.gl.blurend_frame).place(x=xx + 165, y=yy)

        self.blur_preview = Label(blur_effect_labelrame, bg=self.gl.bkcolor, relief=RAISED, image=self.gl.preview_image)
        self.blur_preview.place(x=360, y=10)

    def load_glow_shape(self):
        """
        Load a new shape(image) and convert it to a Tkinter image and create a pygame reference too
        Display the image to the preview tkinter label

        :return: None
        """
        filename = filedialog.askopenfilename(
            initialdir=self.gl.path, title="Select a shape", filetypes=self.gl.file_format)

        try:
            glow_shape = Image.open(filename)
            glow_shape = glow_shape.resize((64, 64))
            self.gl.glow_shape_pygame = pygame.image.load(filename).convert()
            self.gl.glow_shape_pygame = pygame.transform.smoothscale(self.gl.glow_shape_pygame, (64, 64))

        except Exception as e:
            messagebox.showerror("Error", "Cannot open file : %s\nError code %s " % (filename, e))
            return
        self.blend_shape(self.gl.glow_scale_value.get())
        # self.gl.glow_shape = ImageTk.PhotoImage(glow_shape)
        # self.glow_shape_preview.config(image=self.gl.glow_shape)

    def blend_shape(self, scale_value_):
        """
        Create and display the preview image of the shape after rotating the hue
        This method is used by the glow effect.
        A copy of the original pygame surface is created before altering the surface with hue rotation

        * scale value is within the range [-180.0 ... +180.0] and controlled by the tkinter scale

        :param scale_value_: float; Value within range [-180.0 ... +180.0]
        :return: None
        """

        surface = self.gl.glow_shape_pygame.copy()

        value = (int(scale_value_) + 180.0) / 360.0
        surface = hsv_surface24c(surface, value)

        # CONVERT PYGAME TO TKINTER IMAGE
        image_str = pygame.image.tostring(surface, 'RGBA')
        w, h = surface.get_rect()[2:]
        image = Image.frombytes('RGBA', (w, h), image_str)

        self.gl.glow_shape = ImageTk.PhotoImage(image)
        self.glow_shape_preview.config(image=self.gl.glow_shape)

    def glow_effect(self):

        glow_effect_labelframe = LabelFrame(
            self.effect_labelframe, text="Glow", bg=self.gl.bkcolor, width=475, height=110, bd=2)
        glow_effect_labelframe.place(x=0, y=485)

        glow = Checkbutton(
            glow_effect_labelframe, text='Glow', bg=self.gl.bkcolor, variable=self.gl.glow_checkbox,
            onvalue=1, offvalue=0, command=dummy)
        glow.place(x=5, y=25)
        glow_checkbutton_ballon = Pmw.Balloon(self.root)
        glow_checkbutton_ballon.bind(glow, "Enable glowing effect")

        Label(glow_effect_labelframe, text="Direction", bg=self.gl.bkcolor).place(x=70, y=0)

        # def TextBoxUpdate(value_):
        #     if self.gl.glow_direction.get() == "up":
        #         print("up")
        #     elif self.gl.glow_direction.get() == "down":
        #         print("down")

        self.gl.glow_direction = ttk.Combobox(
            glow_effect_labelframe, text='Glow',
            textvariable=self.gl.glow_var, state='readonly', width=10)
        # self.gl.glow_direction.bind("<<ComboboxSelected>>", TextBoxUpdate)
        direction_checkbutton_ballon = Pmw.Balloon(self.root)
        direction_checkbutton_ballon.bind(
            self.gl.glow_direction, "Choose a glowing direction\nAdjust the shape according to the direction\n"
                                    "Load icon_glareFx_red.png for left or right direction\n"
                                    "Load icon_glareFx_blue.png for up and down direction")
        self.gl.glow_direction.place(x=70, y=25)
        self.gl.glow_direction.config(values=["right", "left", "up", "down", "top_l to bottom_r", 'top_r to bottom_l'])
        self.gl.glow_direction.current(0)

        # def blend_shape(scale_value_):
        #     """
        #     Create and display the preview image of the shape after rotating the hue
        #     This method is used by the glow effect.
        #     A copy of the original pygame surface is created before altering the surface with hue rotation
        #
        #     * scale value is within the range [-180.0 ... +180.0] and controlled by the tkinter scale
        #
        #     :param scale_value_: float; Value within range [-180.0 ... +180.0]
        #     :return: None
        #     """
        #
        #     surface = self.gl.glow_shape_pygame.copy()
        #
        #     value = (int(scale_value_) + 180.0) / 360.0
        #     surface = hsv_surface24c(surface, value)
        #
        #     # CONVERT PYGAME TO TKINTER IMAGE
        #     image_str = pygame.image.tostring(surface, 'RGBA')
        #     w, h = surface.get_rect()[2:]
        #     image = Image.frombytes('RGBA', (w, h), image_str)
        #
        #     self.gl.glow_shape = ImageTk.PhotoImage(image)
        #     self.glow_shape_preview.config(image=self.gl.glow_shape)

        glow_scale = Scale(
            glow_effect_labelframe, bg=self.gl.bkcolor, orient=HORIZONTAL, bd=2, relief=FLAT,
            activebackground=self.gl.bkcolor, troughcolor="LIGHTGRAY", variable=self.gl.glow_scale_value,
            length=180, highlightbackground=self.gl.bkcolor, from_=-180, to_=180, width=10, command=self.blend_shape)
        glow_scale.place(x=160, y=30)
        glow_scale_ballon = Pmw.Balloon(self.root)
        glow_scale_ballon.bind(glow_scale, "Hue the texture from -180 to +180")

        self.glow_shape_preview = Label(glow_effect_labelframe, bg=self.gl.bkcolor,
                                        relief=RAISED, image=self.gl.glow_shape)
        self.glow_shape_preview.place(x=360, y=10)

        shape = Button(
            glow_effect_labelframe, text="shape", width=7, height=1,
            bg=self.gl.bkcolor, command=lambda: self.load_glow_shape())
        shape.place(x=230, y=5)
        shape_ballon = Pmw.Balloon(self.root)
        shape_ballon.bind(shape, "Load a specific image for the glowing shape\n"
                                 "Compatible with image format PNG, JPG, GIF\n"
                                 "Load icon_glareFx_red.png for left or right direction\n"
                                 "Load icon_glareFx_blue.png for up and down direction")

    def channel_get_mode(self):
        # TODO FIND A BETTER WAY
        mode = self.channel_conversion.get()
        channels = {'R': self.gl.red_channel.get(), 'G': self.gl.green_channel.get(), 'B': self.gl.blue_channel.get()}
        mode_list = {mode[0]: 1, mode[1]: 1, mode[2]: 1}

        if len(mode) != 0:
            for letter in mode:
                if channels[letter] == 1:
                    continue
                else:
                    mode_list[letter] = 0
        string = ""

        for letter in mode:
            if mode_list[letter] == 0:
                string += '0'
            else:
                string += str(letter)
        return string

    def channels_preview_update(self):
        if not (isinstance(self.gl.pyimage, list) and len(self.gl.pyimage) != 0):
            return

        pyimage = self.gl.pyimage[0]

        if self.gl.input_format_24bit.get():
            pyimage = swap_channels24_c(pyimage, self.channel_get_mode())
            pyimage = pygame.transform.smoothscale(pyimage, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.rgb_channel_preview.image = tkinter_image
            self.rgb_channel_preview.config(image=tkinter_image)
            self.rgb_channel_preview.update()

        else:
            pyimage = swap_channels32_c(pyimage, self.channel_get_mode())
            pyimage = pygame.transform.smoothscale(pyimage, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.rgb_channel_preview.image = tkinter_image
            self.rgb_channel_preview.config(image=tkinter_image)
            self.rgb_channel_preview.update()

    def rgb_channel_effect(self):

        rgb_channels_labelframe = LabelFrame(
            self.effect_labelframe, text="RGB channels", bg=self.gl.bkcolor, width=475, height=110, bd=2)
        rgb_channels_labelframe.place(x=0, y=600)

        channels_checkbutton = Checkbutton(
            rgb_channels_labelframe, text='Channels', bg=self.gl.bkcolor, variable=self.gl.channel_checkbox,
            onvalue=1, offvalue=0, command=dummy)
        channels_checkbutton.place(x=5, y=25)
        channels_balloon = Pmw.Balloon(self.root)
        channels_balloon.bind(channels_checkbutton, "Select RGB channels effect")

        def validate_data_channel(w):
            self.channels_preview_update()
            return True

        vcmd_channel = (rgb_channels_labelframe.register(validate_data_channel), '%V')

        Label(rgb_channels_labelframe, text="conversion mode", bg=self.gl.bkcolor).place(x=90, y=0)

        self.channel_conversion = ttk.Combobox(
            rgb_channels_labelframe, textvariable=self.gl.widget_var,
            values=["RGB", "RBG", "GRB", "BRG", "BGR", "GBR"], state='readonly', width=10,
            justify='left', validate='all', validatecommand=vcmd_channel)
        self.channel_conversion.current(0)
        self.channel_conversion.place(x=90, y=25)
        channels_conversion_balloon = Pmw.Balloon(self.root)
        channels_conversion_balloon.bind(self.channel_conversion, "Select image format")

        active_channels = LabelFrame(
            rgb_channels_labelframe, text="Active channels", bg=self.gl.bkcolor,
            width=130, height=60, bd=2)
        active_channels.place(x=200, y=5)

        red_channel = Checkbutton(
            active_channels, text='R', bg=self.gl.bkcolor, variable=self.gl.red_channel, onvalue=1,
            offvalue=0, command=self.channels_preview_update)
        red_channel.place(x=5, y=5)
        red_channel_balloon = Pmw.Balloon(self.root)
        red_channel_balloon.bind(red_channel, "Select or unselect the red channel")

        green_channel = Checkbutton(
            active_channels, text='G', bg=self.gl.bkcolor, variable=self.gl.green_channel, onvalue=1,
            offvalue=0, command=self.channels_preview_update)
        green_channel.place(x=45, y=5)
        green_channel_balloon = Pmw.Balloon(self.root)
        green_channel_balloon.bind(green_channel, "Select or unselect the green channel")

        blue_channel = Checkbutton(
            active_channels, text='B', bg=self.gl.bkcolor, variable=self.gl.blue_channel,
            onvalue=1, offvalue=0, command=self.channels_preview_update)
        blue_channel.place(x=85, y=5)
        blue_channel_balloon = Pmw.Balloon(self.root)
        blue_channel_balloon.bind(blue_channel, "Select or unselect the blue channel")

        self.rgb_channel_preview = Label(rgb_channels_labelframe, bg=self.gl.bkcolor,
                                         relief=RAISED, image=self.gl.preview_image)
        self.rgb_channel_preview.place(x=360, y=10)

    def rgb_split_preview_update(self):

        if not (isinstance(self.gl.pyimage, list) and len(self.gl.pyimage) != 0):
            return

        pyimage = self.gl.pyimage[0]

        x_offset = int(self.gl.rgbsplitxoffset.get())
        y_offset = int(self.gl.rgbsplityoffset.get())
        w, h = pyimage.get_size()

        if self.gl.input_format_24bit.get():
            new_surface = pygame.Surface((w + 2 * x_offset, h + 2 * y_offset))
            new_surface.fill((0, 0, 0, 0))
            surf = new_surface

            red_layer, green_layer, blue_layer = rgb_split_channels(pyimage)
            if self.gl.split_red_checkbox.get() == 1:
                surf.blit(red_layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            if self.gl.split_green_checkbox.get() == 1:
                surf.blit(green_layer, (x_offset, y_offset), special_flags=pygame.BLEND_RGB_ADD)
            if self.gl.split_blue_checkbox.get() == 1:
                surf.blit(blue_layer, (x_offset * 2, y_offset * 2),
                          special_flags=pygame.BLEND_RGB_ADD)

            pyimage = pygame.transform.smoothscale(surf, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.rgbsplit_preview.image = tkinter_image
            self.rgbsplit_preview.config(image=tkinter_image)
            self.rgbsplit_preview.update()

        else:
            new_surface = pygame.Surface((w + 2 * x_offset, h + 2 * y_offset), pygame.SRCALPHA)
            new_surface.fill((0, 0, 0, 0))
            new_surface = new_surface.convert_alpha()

            red_layer, green_layer, blue_layer = rgb_split_channels_alpha(pyimage)
            if self.gl.split_red_checkbox.get() == 1:
                new_surface.blit(red_layer, (0, 0))
            if self.gl.split_green_checkbox.get() == 1:
                new_surface.blit(green_layer.convert_alpha(), (x_offset, y_offset), special_flags=pygame.BLEND_RGB_ADD)
            if self.gl.split_blue_checkbox.get() == 1:
                new_surface.blit(blue_layer.convert_alpha(),
                                 (x_offset * 2, y_offset * 2), special_flags=pygame.BLEND_RGB_ADD)
            #
            self.refresh(new_surface)
            new_surface = new_surface.convert_alpha()
            pyimage = pygame.transform.smoothscale(new_surface, (64, 64))

            # CONVERT PYGAME SURFACE TO TKINTER PHOTOIMAGE
            tkinter_image = pygame_to_tkinter(pyimage, 64, 64)

            self.rgbsplit_preview.image = tkinter_image
            self.rgbsplit_preview.config(image=tkinter_image)
            self.rgbsplit_preview.update()

    def rgb_split_effect(self):

        rgpsplit_labelframe = LabelFrame(
            self.effect_labelframe, text="RGB split", bg=self.gl.bkcolor,
            width=475, height=110, bd=2)
        rgpsplit_labelframe.place(x=480, y=5)

        self.rgb_split = Checkbutton(
            rgpsplit_labelframe, text='RGB split', bg=self.gl.bkcolor, variable=self.gl.rgbsplit_checkbox,
            onvalue=1, offvalue=0, command=dummy)
        self.rgb_split.place(x=5, y=25)
        rgb_split_balloon = Pmw.Balloon(self.root)
        rgb_split_balloon.bind(self.rgb_split, "Create RGB split effect")

        Label(rgpsplit_labelframe, bg=self.gl.bkcolor, text="x offset").place(x=80, y=10)
        x_offset = Entry(rgpsplit_labelframe, width=4, bd=2, textvariable=self.gl.rgbsplitxoffset)
        x_offset.place(x=130, y=10)
        x_offset.bind('<FocusOut>', lambda event: self.rgb_split_preview_update())
        x_offset_balloon = Pmw.Balloon(self.root)
        x_offset_balloon.bind(x_offset, "X offset for layer RGB")

        Label(rgpsplit_labelframe, bg=self.gl.bkcolor, text="y offset").place(x=80, y=40)
        y_offset = Entry(rgpsplit_labelframe, validate="key", width=4, bd=2, textvariable=self.gl.rgbsplityoffset)
        y_offset.place(x=130, y=40)
        y_offset.bind('<FocusOut>', lambda event: self.rgb_split_preview_update())
        y_offset_balloon = Pmw.Balloon(self.root)
        y_offset_balloon.bind(y_offset, "Y offset for layer RGB")

        split_red = Checkbutton(
            rgpsplit_labelframe, text='Red', bg=self.gl.bkcolor, variable=self.gl.split_red_checkbox,
            onvalue=1, offvalue=0, command=self.rgb_split_preview_update)
        split_red.place(x=180, y=5)
        split_red_balloon = Pmw.Balloon(self.root)
        split_red_balloon.bind(split_red, "Split red channel")

        split_green = Checkbutton(
            rgpsplit_labelframe, text='Green', bg=self.gl.bkcolor, variable=self.gl.split_green_checkbox,
            onvalue=1, offvalue=0, command=self.rgb_split_preview_update)
        split_green.place(x=180, y=25)
        split_green_balloon = Pmw.Balloon(self.root)
        split_green_balloon.bind(split_green, "Split green channel")

        split_blue = Checkbutton(
            rgpsplit_labelframe, text='Blue', bg=self.gl.bkcolor, variable=self.gl.split_blue_checkbox,
            onvalue=1, offvalue=0, command=self.rgb_split_preview_update)
        split_blue.place(x=180, y=45)
        split_blue_balloon = Pmw.Balloon(self.root)
        split_blue_balloon.bind(split_blue, "Split blue channel")

        self.rgbsplit_preview = Label(
            rgpsplit_labelframe, bg=self.gl.bkcolor, relief=RAISED, image=self.gl.preview_image)
        self.rgbsplit_preview.place(x=360, y=10)

        Label(rgpsplit_labelframe, text="Start frame", bg=self.gl.bkcolor).place(x=240, y=10)
        Entry(rgpsplit_labelframe, validate="key", width=4, bd=2,
              textvariable=self.gl.rgbsplit_start_frame).place(x=310, y=10)

        Label(rgpsplit_labelframe, text="End frame", bg=self.gl.bkcolor).place(x=240, y=45)
        Entry(rgpsplit_labelframe, validate="key", width=4, bd=2,
              textvariable=self.gl.rgbsplit_end_frame).place(x=310, y=45)

    def transition_effect(self):

        transition_labelframe = LabelFrame(self.effect_labelframe, text="Transition", bg=self.gl.bkcolor,
                                           width=475, height=110, bd=2)
        transition_labelframe.place(x=480, y=125)

        transition = Checkbutton(
            transition_labelframe, text='Transition', bg=self.gl.bkcolor, variable=self.gl.transition_checkbox,
            onvalue=1, offvalue=0, command=dummy)
        transition.place(x=5, y=25)
        transition_checkbutton_ballon = Pmw.Balloon(self.root)
        transition_checkbutton_ballon.bind(transition, "Enable transition effect")

        def load_transition_texture():

            filename = filedialog.askopenfilename(
                initialdir=self.gl.path, title="Select a shape",
                filetypes=self.gl.file_format)

            try:
                self.gl.transition_texture = pygame.image.load(filename).convert_alpha()

            except Exception as error:
                messagebox.showerror("Error", "Cannot open file : %s\nError: %s " % (filename, error))
                return

        texture = Button(
            transition_labelframe, text="Texture",
            width=7, height=1, bg=self.gl.bkcolor, command=lambda: load_transition_texture())
        texture.place(x=90, y=25)
        texture_checkbutton_ballon = Pmw.Balloon(self.root)
        texture_checkbutton_ballon.bind(texture, "Load an image for the transition effect.\n"
                                                 "The sprites will progressively blend toward\n"
                                                 "the loaded image.")

        # Checkbutton(
        #     transition_labelframe, text='Alpha 1', bg=self.gl.bkcolor,
        #     variable=self.gl.transition_alpha1, onvalue=1, offvalue=0, command=dummy).place(x=160, y=5)
        #
        # Checkbutton(transition_labelframe, text='Alpha 2', bg=self.gl.bkcolor, variable=self.gl.transition_alpha2,
        #             onvalue=1, offvalue=0, command=dummy).place(x=160, y=45)

        self.transition_preview = Label(
            transition_labelframe, bg=self.gl.bkcolor, relief=RAISED, image=self.gl.preview_image)
        self.transition_preview.place(x=360, y=10)

        Label(transition_labelframe, text="Start frame", bg=self.gl.bkcolor).place(x=240, y=10)
        Entry(transition_labelframe, validate="key", width=4, bd=2,
              textvariable=self.gl.transition_start_frame).place(x=310, y=10)

        Label(transition_labelframe, text="End frame", bg=self.gl.bkcolor).place(x=240, y=45)
        Entry(transition_labelframe, validate="key", width=4,
              bd=2, textvariable=self.gl.transition_end_frame).place(x=310, y=45)

    def glitch_effect(self):

        glitch_labelframe = LabelFrame(self.effect_labelframe, text="Glitch", bg=self.gl.bkcolor,
                                       width=475, height=110, bd=2)
        glitch_labelframe.place(x=480, y=245)

        glitch = Checkbutton(
            glitch_labelframe, text='Glitch', bg=self.gl.bkcolor, variable=self.gl.glitch_checkbox,
            onvalue=1, offvalue=0, command=dummy)
        glitch.place(x=5, y=25)
        glitch_checkbutton_ballon = Pmw.Balloon(self.root)
        glitch_checkbutton_ballon.bind(glitch, "Enable glitch effect")

        horiz = Checkbutton(
            glitch_labelframe, text='Horizontal', bg=self.gl.bkcolor, variable=self.gl.glitch_horizontal,
            onvalue=1, offvalue=0, command=dummy)
        horiz.place(x=70, y=10)
        horiz_checkbutton_ballon = Pmw.Balloon(self.root)
        horiz_checkbutton_ballon.bind(horiz, "Create an horizontal glitch effect")

        vert = Checkbutton(
            glitch_labelframe, text='Vertical',  bg=self.gl.bkcolor, variable=self.gl.glitch_vertical,
            onvalue=1, offvalue=0, command=dummy)
        vert.place(x=70, y=45)
        vert_checkbutton_ballon = Pmw.Balloon(self.root)
        vert_checkbutton_ballon.bind(vert, "Create an vertical glitch effect")

        self.glitch_preview = Label(glitch_labelframe, bg=self.gl.bkcolor, relief=RAISED, image=self.gl.preview_image)
        self.glitch_preview.place(x=360, y=10)

        Label(glitch_labelframe, text="Start frame", bg=self.gl.bkcolor).place(x=240, y=10)
        Entry(glitch_labelframe, validate="key", width=4, bd=2,
              textvariable=self.gl.glitch_start_frame).place(x=310, y=10)

        Label(glitch_labelframe, text="End frame", bg=self.gl.bkcolor).place(x=240, y=45)
        Entry(glitch_labelframe, validate="key", width=4, bd=2,
              textvariable=self.gl.glitch_end_frame).place(x=310, y=45)

    def miscelleanous_effect(self):
        misc_labelframe = LabelFrame(
            self.effect_labelframe, text="Miscellaneous", bg=self.gl.bkcolor,
            width=475, height=110, bd=2)
        misc_labelframe.place(x=480, y=365)

        # DITHERING
        dithering_labelframe = LabelFrame(
            misc_labelframe, text="dithering", bg=self.gl.bkcolor,  width=110, height=85, bd=2)
        dithering_labelframe.place(x=5, y=0)
        dither = Checkbutton(
            dithering_labelframe, text='dithering', bg=self.gl.bkcolor, variable=self.gl.dithering,
            onvalue=1, offvalue=0, command=dummy)
        dither.place(x=0, y=5)
        dither_entry = Entry(dithering_labelframe, validate="key", width=4, bd=2,
                             textvariable=self.gl.dithering_value)
        dither_entry.place(x=5, y=35)
        dither_checkbutton_ballon = Pmw.Balloon(self.root)
        dither_checkbutton_ballon.bind(
            dither_entry, "Dithered images, particularly those with relatively\n"
            " few colors, can often be distinguished by a characteristic\n"
            " graininess or speckled appearance. Choose a value in range [0 ... 16]")

        # PIXEL
        pixel_labelframe = LabelFrame(misc_labelframe, text="Pixelated", bg=self.gl.bkcolor,
                                      width=150, height=85, bd=2)
        pixel_labelframe.place(x=120, y=0)

        pixel_checkbutton = Checkbutton(
            pixel_labelframe, text='Pixelated', bg=self.gl.bkcolor, variable=self.gl.pixel,
            onvalue=1, offvalue=0, command=dummy)
        pixel_checkbutton.place(x=5, y=5)

        Label(pixel_labelframe, text="pixel block size", bg=self.gl.bkcolor).place(x=5, y=35)
        pixel_width_entry = Entry(pixel_labelframe, validate="key", width=4, bd=2,
                                  textvariable=self.gl.pixel_size)
        pixel_width_entry.place(x=90, y=35)

        pixel_checkbutton_ballon = Pmw.Balloon(self.root)
        pixel_checkbutton_ballon.bind(
            pixel_width_entry, "Pixelate an images\nChoose one of the following values [4, 8, 16, 32, 64]")

        sepia_checkbutton = Checkbutton(
            misc_labelframe, text='Sepia', bg=self.gl.bkcolor, variable=self.gl.sepia,
            onvalue=1, offvalue=0, command=dummy)
        sepia_checkbutton.place(x=300, y=15)

        gray_checkbutton = Checkbutton(
            misc_labelframe, text='Greyscale', bg=self.gl.bkcolor, variable=self.gl.greyscale,
            onvalue=1, offvalue=0, command=dummy)
        gray_checkbutton.place(x=300, y=40)

    def preview_options(self):
        preview_label = LabelFrame(self.root, text="Preview options", bg=self.gl.bkcolor, width=475, height=160, bd=2)
        preview_label.place(x=5, y=635)

        def show_milliseconds(scale_value):

            v = int(scale_value)
            if not isinstance(v, int):
                return
            if v == 0:
                return

            tick = int(float(1 / v) * 1000)
            fps.config(text="%s msecs" % tick)

            if isinstance(self.gl.pyimage, list):
                frames = len(self.gl.pyimage)
                t = round(((1/v) * frames), 3)
                self.duration.config(text=str(t))
            else:
                return

        fps = Label(preview_label, text="fps: ", bg="#858585")
        fps.place(x=190, y=50)

        Label(preview_label, text="Frame number :", bg="#858585").place(x=5, y=80)
        self.frame_number = Label(preview_label, text="0", bg="#858585")
        self.frame_number.place(x=100, y=80)

        Label(preview_label, text="Duration in secs :", bg="#858585").place(x=5, y=100)
        self.duration = Label(preview_label, text="0", bg="#858585")
        self.duration.place(x=100, y=100)

        self.preview_delay_value = Scale(
            preview_label, bg="#858585", orient=HORIZONTAL, bd=2, relief=FLAT,
            activebackground="#858585", troughcolor="#858585", variable=self.gl.preview_scale_delay, length=180,
            highlightbackground="#858585", from_=1, to_=200, width=10, command=show_milliseconds)
        self.preview_delay_value.place(x=5, y=35)
        preview_delay_value_balloon = Pmw.Balloon(self.root)
        preview_delay_value_balloon.bind(self.preview_delay_value, "Adjust the FPS, default 60 frames per seconds")

        show_milliseconds(self.gl.preview_scale_delay.get())

        self.preview_button = Button(
            preview_label, text="Apply / Preview", width=20, height=1, bg="#858585",
            command=lambda: self.preview(int(self.preview_delay_value.get())))
        self.preview_button.place(x=10, y=5)
        preview_button_balloon = Pmw.Balloon(self.root)
        preview_button_balloon.bind(self.preview_button, "Preview effect(s) on canvas and pygame display")
        self.preview_button.config(state=DISABLED)

        self.checker_background_value = Checkbutton(
            preview_label, text='Checker bck', bg="#858585", variable=self.gl.checker_value, onvalue=1, offvalue=0)
        self.checker_background_value.place(x=250, y=110)
        checker_balloon = Pmw.Balloon(self.root)
        checker_balloon.bind(
            self.checker_background_value,
            "Display a checker background during the \n"
            "rendering (only for 32-bit image format)")

        inverse_labelframe = LabelFrame(
            preview_label, text="Inverse", bg=self.gl.bkcolor, width=200, height=110, bd=2)
        inverse_labelframe.place(x=250, y=0)

        inverse_checkbox = Checkbutton(
            inverse_labelframe, text='Inverse', bg="#858585", variable=self.gl.inverse_variable, onvalue=1, offvalue=0)
        inverse_checkbox.place(x=0, y=15)
        inverse_balloon = Pmw.Balloon(self.root)
        inverse_balloon.bind(
            inverse_checkbox, "Inverse (negative) effect apply to all texture")

        def exc_button_state():
            if self.gl.inverse_exclude_variable.get():
                self.exclude_button_inv.configure(state="normal")
                self.exclude_red_entry.configure(state="normal")
                self.exclude_green_entry.configure(state="normal")
                self.exclude_blue_entry.configure(state="normal")
            else:
                self.exclude_button_inv.configure(state="disabled")
                self.exclude_red_entry.configure(state="disabled")
                self.exclude_green_entry.configure(state="disabled")
                self.exclude_blue_entry.configure(state="disabled")

        inverse_exclude_checkbox = Checkbutton(
            inverse_labelframe, text='Exclude', bg="#858585",
            variable=self.gl.inverse_exclude_variable, onvalue=1, offvalue=0, command=exc_button_state)
        inverse_exclude_checkbox.place(x=0, y=45)
        inverse_exclude_balloon = Pmw.Balloon(self.root)
        inverse_exclude_balloon.bind(
            inverse_exclude_checkbox, "Exclude a specific color for the inverse effect")

        # Label(inverse_labelframe, text="Exclude", bg=self.gl.bkcolor).place(x=75, y=0)
        Label(inverse_labelframe, text="Red", bg=self.gl.bkcolor).place(x=75, y=0)
        Label(inverse_labelframe, text="Green", bg=self.gl.bkcolor).place(x=75, y=30)
        Label(inverse_labelframe, text="Blue", bg=self.gl.bkcolor).place(x=75, y=60)
        self.exclude_red_entry = Entry(
            inverse_labelframe, validate="key", width=4, bd=2, textvariable=self.gl.exclude_red_inv, state=DISABLED)
        self.exclude_red_entry.place(x=115, y=0)
        self.exclude_green_entry = Entry(
            inverse_labelframe, validate="key", width=4, bd=2, textvariable=self.gl.exclude_green_inv, state=DISABLED)
        self.exclude_green_entry.place(x=115, y=30)
        self.exclude_blue_entry = Entry(
            inverse_labelframe, validate="key", width=4, bd=2, textvariable=self.gl.exclude_blue_inv, state=DISABLED)
        self.exclude_blue_entry.place(x=115, y=60)

        self.exclude_button_inv = Button(
            inverse_labelframe, text="Edit colors", image=self.gl.color_icon, state=DISABLED,
            command=lambda: select_color(self.gl.exclude_red_inv, self.gl.exclude_green_inv, self.gl.exclude_blue_inv))
        self.exclude_button_inv.place(x=155, y=30)

    def effects_frame(self):
        self.effect_labelframe = LabelFrame(self.root, text="EFFECTS", bg="#858585", width=980, height=790, bd=2)
        self.effect_labelframe.place(x=480, y=5)

    def dummy(self):
        pass

    def save_as_spritesheet(self):
        pass

    def close(self):
        pass

    @staticmethod
    def about():
        global VERSION
        messagebox.showinfo(
            "", "SpriteStudio version %s\n\n"
            "This software is a free software release under the GNU license\n"
            "SpriteStudio is free software: you can redistribute it and/or\n"
            "modify it under the terms of the GNU General Public License\n"
            "as published by the Free Software Foundation;\n\n"
            "SpriteStudio is distributed in the hope that it will be useful,\n"
            "but WITHOUT ANY WARRANTY; without even the implied\n"
            "warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n"
            "See the GNU General Public License for more details.\n"                 
            "You should have received a copy of the GNU General Public\n"
            "License along with SpriteStudio.\n"
            "If not see: https://www.gnu.org/licenses/\n\n"
            "Yoann Berenguer All right reserved\n"
            "yoyoberenguer@hotmail.com" % VERSION)
    """
    SpriteStudio is free software: you can redistribute it and/or modify it under the 
    terms of the GNU General Public License as published by the Free Software Foundation;
    either version 3 of the License, or (at your option) any later version.
    SpriteStudio is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with GIMP. If not,
    see: https://www.gnu.org/licenses/
    """

    def draw_menu(self):
        local_dummy = self.dummy
        self.root.configure(background="#4d4d4d")

        menubar \
            = tkinter.Menu(self.root)
        filemenu = tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_spritesheet)
        filemenu.add_command(label="Save", command=self.save_spritesheet)

        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tkinter.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=local_dummy)
        helpmenu.add_command(label="About...", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.root.config(menu=menubar)

    def add_blend_effect(self, top, progress, progress_label, pyimage_copy):
        """
        RETURN THE A LIST OF SURFACES WITH THE ADDITIONAL EFFECT (BLEND) OR RETURN PYIMAGE_COPY UNCHANGED

        :param top: tkinter toplevel window; This window will be used for displaying the overall process
        :param progress: ttk progressbar; Bar showing the overall process
        :param progress_label: tkinter label showing the name of the effect, here blend effect
        :param pyimage_copy: Python list containing all the pygame surfaces to be processed
        :return: Return a list containing all the pygame surface post processing or unchanged if an error occur.
        """
        # SAVE THE SURFACE PRIOR BLENDING
        pyimage_post_processing = pyimage_copy.copy()

        if self.blend_checkbox.get() is True:

            percentage = self.gl.blend_scale_percentage.get()

            if not isinstance(percentage, float):
                messagebox.showwarning(
                    "Warning", "Blend scale percentage type is invalid\n"
                               "Expecting a float got %s\nBlending effect will be disregarded" % type(percentage))
                return pyimage_post_processing

            normalize_value = percentage / 100.0

            if normalize_value > 1.0:
                normalize_value = 1.0
            elif normalize_value < 0.0:
                normalize_value = 0.0

            try:
                red = self.gl.red.get()
                green = self.gl.green.get()
                blue = self.gl.blue.get()
            except:
                messagebox.showwarning("Error", "Blending effect\nBlend With;\n"
                                                "Incorrect values for blending colors red, green or blue")
                return pyimage_post_processing

            try:
                excl_red = self.gl.exclude_red.get()
                excl_green = self.gl.exclude_green.get()
                excl_blue = self.gl.exclude_blue.get()

            except:
                messagebox.showwarning(
                    "Error", "Blending effect\nExclude colors;\nIncorrect exclude colors red, green or blue")
                return pyimage_post_processing

            if isinstance(excl_red, int) and isinstance(excl_green, int) and isinstance(excl_blue, int):
                excl_red = min(excl_red, 255)
                excl_red = max(excl_red, 0)
                excl_green = min(excl_green, 255)
                excl_green = max(excl_green, 0)
                excl_blue = min(excl_blue, 255)
                excl_blue = max(excl_blue, 0)
            else:

                messagebox.showwarning(
                    "Warning", "Blending color excl_red, excl_green or exc_blue are incorrect types\n"
                               "Expecting floats got red %s green %s blue %s\n"
                               "Blending effect will be disregarded" %
                               (type(excl_red), type(excl_green), type(excl_blue)))
                return pyimage_post_processing

            if isinstance(red, int) and isinstance(green, int) and isinstance(blue, int):
                if red < 0:
                    red = 0
                if red > 255:
                    red = 255

                if green < 0:
                    green = 0
                if green > 255:
                    green = 255

                if blue < 0:
                    blue = 0
                if blue > 255:
                    blue = 255
            else:
                messagebox.showwarning(
                    "Warning", "Blending color red, green or blue has an incorrect type\n"
                               "Expecting floats got red %s green %s blue %s\n"
                               "Blending effect will be disregarded" % (type(red), type(green), type(blue)))
                return pyimage_post_processing

            try:
                start = int(self.gl.blend_start_frame.get())
            except:
                messagebox.showwarning("Error", "Blending effect\nIncorrect start frame value")
                return pyimage_post_processing

            try:
                end = int(self.gl.blend_end_frame.get())
            except:
                messagebox.showwarning("Error", "Blending effect\nIncorrect end frame value")
                return pyimage_post_processing

            if start < 0:
                start = 0
            if end > len(self.gl.pyimage):
                end = len(self.gl.pyimage)

            if start > end:
                messagebox.showwarning("Warning", "Blend start frame cannot be > end frame\n"
                                                  "Please adjust the frames values")
                return pyimage_post_processing

            if end < start:
                messagebox.showwarning("Warning", "Blend end frame cannot be < start frame\n"
                                                  "Please adjust the frames values")
                return pyimage_post_processing

            color = (red, green, blue)
            exclude_color = (excl_red, excl_green, excl_blue)

            if bool(self.gl.input_format_32bit.get()):
                # print("Adding blend effect for 32-bit format image...")
                for i in range(start, end):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='blend effect')
                        progress['value'] = i * 400 / (end - start)
                        progress.update()
                        top.update_idletasks()

                        pyimage_copy[i] = blend_texture_32c(pyimage_copy[i], color, percentage)
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred while blending the "
                                     "texture with a pygame surface.\nError : %s" % error)
                        return pyimage_post_processing

            elif bool(self.gl.input_format_24bit.get()):
                # print("Adding blend effect for 24-bit format image...")
                for i in range(start, end):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='blend effect')
                        progress['value'] = i * 400 / (end - start)
                        progress.update()
                        top.update_idletasks()

                        pyimage_copy[i] = blend_texture_24_alpha(
                            pyimage_copy[i], normalize_value, color, exclude_color)

                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred while blending the "
                                     "texture with a pygame surface.\nError : %s" % error)
                        return pyimage_post_processing
        return pyimage_copy

    def add_hsv_effect(self, top, progress, progress_label, pyimage_copy):
        """
        RETURN THE A LIST OF SURFACES WITH THE ADDITIONAL EFFECT (HSV) OR RETURN PYIMAGE_COPY UNCHANGED

        :param top: tkinter toplevel window; This window will be used for displaying the overall process
        :param progress: ttk progressbar; Bar showing the overall process
        :param progress_label: tkinter label showing the name of the effect, here hsv effect
        :param pyimage_copy: Python list containing all the pygame surfaces to be processed
        :return: Return a list containing all the pygame surface post processing or unchanged if an error occur.
        """

        # SAVE THE SURFACE PRIOR HSV
        pyimage_post_processing = pyimage_copy.copy()

        if self.gl.hsv_checkbox.get() is True:

            try:
                start = int(self.gl.hsvstart_frame.get())
            except:
                messagebox.showwarning("Error", "Hsv effect\nIncorrect start frame value")
                return pyimage_post_processing

            try:
                end = int(self.gl.hsvend_frame.get())
            except:
                messagebox.showwarning("Error", "Hsv effect\nIncorrect end frame value")
                return pyimage_post_processing

            if start < 0:
                start = 0
            if end > len(self.gl.pyimage):
                end = len(self.gl.pyimage)

            if start > end:
                messagebox.showwarning("Warning", "HSV start frame cannot be > end frame\n"
                                                  "Please adjust the frames values")
                return pyimage_post_processing

            if end < start:
                messagebox.showwarning("Warning", "HSV end frame cannot be < start frame\n"
                                                  "Please adjust the frames values")
                return pyimage_post_processing

            if start < 0:
                start = 0
            if end > len(self.gl.pyimage):
                end = len(self.gl.pyimage)

            hsv = self.gl.hsv_scale_value.get()
            if not isinstance(hsv, float):
                messagebox.showwarning(
                    "Warning", "HSV scale variable type is invalid\n"
                               "Expecting a float got %s\nHSV effect will be disregarded" % type(hsv))
                return pyimage_post_processing

            normalize_value = (int(hsv) + 180) / 360.0

            rotate = self.gl.hsv_rotate.get()
            if not isinstance(rotate, bool):
                messagebox.showwarning(
                    "Warning", "HSV hsv_rotate variable type is invalid\n"
                               "Expecting a boolean got %s\nHSV effect will be disregarded" % type(rotate))
                return pyimage_post_processing

            if self.gl.input_format_32bit.get():
                # print("Adding HSV (hue rotation) for 32-bit format image...")

                if rotate:
                    if end == 0:
                        return pyimage_post_processing

                    n = 1.0 / float(end)
                    deg = 0
                    for i in range(0, end):
                        try:
                            if self.gl.cancel:
                                raise Exception("Process aborted by user")

                            progress_label.configure(text='hsv effect')
                            progress['value'] = i * 400 / end
                            progress.update()
                            top.update_idletasks()

                            pyimage_copy[i] = hsv_surface32c(pyimage_copy[i], deg)
                        except Exception as error:
                            messagebox.showerror(
                                "Error", "An error occurred while processing hue shifting, "
                                         "method hsv_surface32c.\nError %s" % error)
                            return pyimage_post_processing
                        deg += n

                else:
                    for i in range(start, end):
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")
                        try:
                            progress_label.configure(text='hsv effect')
                            progress['value'] = i * 400 / (end - start)
                            progress.update()
                            top.update_idletasks()
                            pyimage_copy[i] = hsv_surface32c(pyimage_copy[i], normalize_value)
                        except Exception as error:
                            messagebox.showerror(
                                "Error", "An error occurred while processing hue shifting, "
                                         "method hsv_surface32c.\nError %s" % error)
                            return pyimage_post_processing

            else:
                # print("Adding HSV (hue rotation) for 24-bit format image...")
                if rotate:
                    if end == 0:
                        self.preview_button.config(state="normal")
                        self.preview_button.update()
                        return pyimage_post_processing
                    n = 1.0 / float(end)
                    deg = 0
                    for i in range(0, end):
                        try:
                            if self.gl.cancel:
                                raise Exception("Process aborted by user")

                            progress_label.configure(text='hsv effect')
                            progress['value'] = i * 400 / end
                            progress.update()
                            top.update_idletasks()

                            pyimage_copy[i] = hsv_surface24c(pyimage_copy[i], deg)
                        except Exception as error:
                            messagebox.showerror(
                                "Error", "An error occurred while processing hue shifting, "
                                         "method hsv_surface24c.\nError %s" % error)
                            return pyimage_post_processing
                        deg += n

                else:
                    for i in range(start, end):
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")
                        try:
                            progress_label.configure(text='hsv effect')
                            progress['value'] = i * 400 / (end - start)
                            progress.update()
                            top.update_idletasks()
                            pyimage_copy[i] = hsv_surface24c(pyimage_copy[i], normalize_value)
                        except Exception as error:
                            messagebox.showerror(
                                "Error", "An error occurred while processing hue shifting, "
                                         "method hsv_surface24c.\nError %s" % error)
                            return pyimage_post_processing

        return pyimage_copy

    def add_bloom_effect(self, top, progress, progress_label, pyimage_copy):
        """
        RETURN THE A LIST OF SURFACES WITH THE ADDITIONAL EFFECT (BLOOM) OR RETURN PYIMAGE_COPY UNCHANGED

        :param top: tkinter toplevel window; This window will be used for displaying the overall process
        :param progress: ttk progressbar; Bar showing the overall process
        :param progress_label: tkinter label showing the name of the effect, here bloom effect
        :param pyimage_copy: Python list containing all the pygame surfaces to be processed
        :return: Return a list containing all the pygame surface post processing or unchanged if an error occur.
        """

        # SAVE THE SURFACE PRIOR BLOOM
        pyimage_post_processing = pyimage_copy.copy()

        if self.gl.bloom_checkbox.get() is True:

            try:
                start = self.gl.bloomstart_frame.get()
            except:
                messagebox.showwarning("Error", "Bloom effect\nIncorrect start frame value")
                return pyimage_post_processing

            try:
                end = self.gl.bloomend_frame.get()
            except:
                messagebox.showwarning("Error", "Bloom effect\nIncorrect end frame value")
                return pyimage_post_processing

            if start < 0:
                start = 0
            if end > len(self.gl.pyimage):
                end = len(self.gl.pyimage)

            if self.gl.input_format_32bit.get():
                # print("Adding bloom effect for 32-bit format image...")
                for i in range(start, end):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='bloom effect')
                        progress['value'] = i * 400 / (end - start)
                        progress.update()
                        top.update_idletasks()

                        pyimage_copy[i] = bloom_effect_array32(
                            pyimage_copy[i], int(self.gl.highpass_filter_value.get()), 1)
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the bloom process\nError: %s\n"
                                     "The bloom effect will be disregarded" % error)
                        return pyimage_post_processing
            else:
                # print("Adding bloom effect for 24-bit format image...")
                for i in range(start, end):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='bloom effect')
                        progress['value'] = i * 400 / (end - start)
                        progress.update()
                        top.update_idletasks()
                        pyimage_copy[i] = bloom_effect_array24(
                            pyimage_copy[i].convert(24), int(self.gl.highpass_filter_value.get()), 1)
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the bloom process\nError: %s\n"
                                     "The bloom effect will be disregarded" % error)

                        return pyimage_post_processing
        return pyimage_copy

    def add_saturation_effect(self, top, progress, progress_label, pyimage_copy):
        """
        RETURN THE A LIST OF SURFACES WITH THE ADDITIONAL EFFECT (SATURATION) OR RETURN PYIMAGE_COPY UNCHANGED

        :param top: tkinter toplevel window; This window will be used for displaying the overall process
        :param progress: ttk progressbar; Bar showing the overall process
        :param progress_label: tkinter label showing the name of the effect, here saturation effect
        :param pyimage_copy: Python list containing all the pygame surfaces to be processed
        :return: Return a list containing all the pygame surface post processing or unchanged if an error occur.
        """

        # SAVE THE SURFACE PRIOR SATURATION
        pyimage_post_processing = pyimage_copy.copy()

        if self.gl.saturation_checkbox.get() is True:

            # print("Adding saturation effect for 32-bit format image...")

            if self.gl.input_format_32bit.get():
                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='saturation effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()
                        rgb_array = pygame.surfarray.array3d(pyimage_copy[i])
                        alpha_array = pygame.surfarray.array_alpha(pyimage_copy[i])
                        pyimage_copy[i] = saturation_array32(
                            rgb_array, alpha_array, float(
                                self.gl.saturation_scale_value.get()), swap_row_column=False)
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the saturation process\nError: %s\n"
                                     "The saturation effect will be disregarded" % error)

                        return pyimage_post_processing

            else:
                # print("Adding saturation effect for 24-bit format image...")
                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='saturation effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()
                        rgb_array = pygame.surfarray.array3d(pyimage_copy[i])
                        pyimage_copy[i] = saturation_array24(
                            rgb_array, float(self.gl.saturation_scale_value.get()), swap_row_column=False)
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the saturation process\nError: %s\n"
                                     "The saturation effect will be disregarded" % error)

                        return pyimage_post_processing

        return pyimage_copy

    def add_cartoon_effect(self, top, progress, progress_label, pyimage_copy):
        """
        RETURN THE A LIST OF SURFACES WITH THE ADDITIONAL EFFECT (CARTOON) OR RETURN PYIMAGE_COPY UNCHANGED

        :param top: tkinter toplevel window; This window will be used for displaying the overall process
        :param progress: ttk progressbar; Bar showing the overall process
        :param progress_label: tkinter label showing the name of the effect, here cartoon effect
        :param pyimage_copy: Python list containing all the pygame surfaces to be processed
        :return: Return a list containing all the pygame surface post processing or unchanged if an error occur.
        """

        # SAVE THE SURFACE PRIOR BLENDING
        pyimage_post_processing = pyimage_copy.copy()

        if self.gl.cartoon_checkbox.get() is True:
            # print("Adding cartoon effect...")

            try:
                threshold = self.gl.cartoon_threshold.get()
            except:
                messagebox.showwarning("Warning", "Cartoon threshold value is invalid must be \n"
                                                  "an integer type in range [0 ... 100].")
                return pyimage_post_processing

            try:
                neighbourhood = self.gl.cartoon_neightboors.get()
                if neighbourhood < 0 or neighbourhood > 16:
                    raise ValueError
            except:
                messagebox.showwarning("Warning", "Cartoon neighbourhood value is invalid.\n"
                                                  "Value must be an integer in range [1 ... 16]")
                return pyimage_post_processing

            try:
                colors = self.gl.cartoon_color.get()
                if colors < 0 or colors > 65535:
                    raise ValueError
            except:
                messagebox.showwarning("Warning", "Cartoon colors value is invalid.\n"
                                                  "Value must be an integer in range [0 ... 65535]")
                return pyimage_post_processing

            if self.gl.input_format_32bit.get():
                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        blur_image = canny_blur5x5_surface32_c(pyimage_copy[i])

                        if self.gl.cartoon_lightness.get():
                            grayscale_image = greyscale_lightness32_c(blur_image)

                        elif self.gl.cartoon_luminosity.get():
                            grayscale_image = greyscale_luminosity32_c(blur_image)

                        else:
                            grayscale_image = greyscale32_c(blur_image)

                        edge_detection_image = sobel32(grayscale_image, threshold)
                        # APPLY THE MEDIAN FILTER
                        if neighbourhood == 0:
                            pyimage_copy[i] = edge_detection_image
                        else:
                            pyimage_copy[i] = median_filter32_c(pyimage_copy[i], neighbourhood)
                            pyimage_copy[i].blit(edge_detection_image, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

                        # APPLY COLOR REDUCTION
                        if not colors == 0:
                            pyimage_copy[i] = color_reduction32_c(pyimage_copy[i], colors)

                        progress_label.configure(text='cartoon effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()

                    except Exception as error:
                        messagebox.showwarning(
                            "Warning", "An error occurred during the cartoon process\nError: %s\n"
                                       "The cartoon effect will be disregarded" % error)
                        return pyimage_post_processing

            else:

                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        blur_image = pygame.surfarray.make_surface(canny_blur5x5_surface24_c(pyimage_copy[i]))

                        if self.gl.cartoon_lightness.get():
                            grayscale_image = greyscale_lightness24_c(blur_image)

                        elif self.gl.cartoon_luminosity.get():
                            grayscale_image = greyscale_luminosity24_c(blur_image)

                        else:
                            grayscale_image = greyscale24_c(blur_image)

                        edge_detection_image = pygame.surfarray.make_surface(sobel24(grayscale_image, threshold))
                        # APPLY THE MEDIAN FILTER
                        if neighbourhood == 0:
                            pyimage_copy[i] = edge_detection_image
                        else:
                            pyimage_copy[i] = median_filter24_c(pyimage_copy[i], neighbourhood)
                            pyimage_copy[i].blit(edge_detection_image, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

                        # APPLY COLOR REDUCTION
                        if not colors == 0:
                            pyimage_copy[i] = color_reduction24_c(pyimage_copy[i], colors)

                        progress_label.configure(text='cartoon effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()

                    except Exception as error:
                        messagebox.showwarning(
                            "Warning", "An error occurred during the cartoon process\nError: %s\n"
                                       "The cartoon effect will be disregarded" % error)
                        return pyimage_post_processing

        return pyimage_copy

    def add_blur_effect(self, top, progress, progress_label, pyimage_copy):
        """
        RETURN THE A LIST OF SURFACES WITH THE ADDITIONAL EFFECT (CARTOON) OR RETURN PYIMAGE_COPY UNCHANGED

        :param top: tkinter toplevel window; This window will be used for displaying the overall process
        :param progress: ttk progressbar; Bar showing the overall process
        :param progress_label: tkinter label showing the name of the effect, here cartoon effect
        :param pyimage_copy: Python list containing all the pygame surfaces to be processed
        :return: Return a list containing all the pygame surface post processing or unchanged if an error occur.
        """

        # SAVE THE SURFACE PRIOR BLUR
        pyimage_post_processing = pyimage_copy.copy()

        if self.gl.blur_checkbox.get() is True:

            try:
                start_ = self.gl.blurstart_frame.get()
            except:
                messagebox.showwarning("Error", "Blur effect\nIncorrect start frame value")
                return pyimage_post_processing

            try:
                end_ = self.gl.blurend_frame.get()
            except:
                messagebox.showwarning("Error", "Blur effect\nIncorrect end frame value")
                return pyimage_post_processing

            start = int(start_)
            end = int(end_)

            if start < 0:
                start = 0
            if start > end:
                messagebox.showwarning("Warning", "Blur start frame cannot be > end frame\n"
                                                  "Please adjust the frames values")
                return pyimage_post_processing

            if end < start:
                messagebox.showwarning("Warning", "Blur end frame cannot be < start frame\n"
                                                  "Please adjust the frames values")
                return pyimage_post_processing

            if end > len(self.gl.pyimage):
                end = len(self.gl.pyimage)

            blurx2 = self.gl.blurx2.get()
            blurx4 = self.gl.blurx4.get()
            blurx6 = self.gl.blurx6.get()

            passes = 1
            if blurx2:
                passes = 2
            if blurx4:
                passes = 4
            if blurx6:
                passes = 6

            if self.gl.input_format_32bit.get():
                # print("Adding blur effect for 32-bit format image...")
                for j in range(passes):
                    for i in range(start, end):

                        try:
                            if self.gl.cancel:
                                raise Exception("Process aborted by user")

                            progress_label.configure(text='blur effect')
                            progress['value'] = i * 400 / (end - start)
                            progress.update()
                            top.update_idletasks()

                            rgb_array = pygame.surfarray.array3d(pyimage_copy[i])
                            alpha_array = pygame.surfarray.array_alpha(pyimage_copy[i])
                            rgba_array = numpy.dstack((rgb_array, alpha_array)).transpose(1, 0, 2)
                            w, h = rgba_array.shape[:2]
                            pyimage_copy[i] = pygame.image.frombuffer(blur5x5_array32(rgba_array), (w, h),
                                                                      'RGBA')
                        except Exception as error:
                            messagebox.showerror(
                                "Error", "An error occurred during the blur process\nError: %s\n"
                                         "The blur effect will be disregarded" % error)
                            return pyimage_post_processing

            else:
                # print("Adding blur effect for 24-bit format image...")
                for _ in range(passes):
                    for i in range(start, end):

                        try:
                            if self.gl.cancel:
                                raise Exception("Process aborted by user")

                            progress_label.configure(text='blur effect')
                            progress['value'] = i * 400 / (end - start)
                            progress.update()
                            top.update_idletasks()
                            rgb_array = pygame.surfarray.array3d(pyimage_copy[i])
                            pyimage_copy[i] = pygame.surfarray.make_surface(
                                numpy.asarray(blur5x5_array24(rgb_array)))
                        except Exception as error:
                            messagebox.showerror(
                                "Error", "An error occurred during the blur process\nError: %s\n"
                                         "The blur effect will be disregarded" % error)
                            return pyimage_post_processing
        return pyimage_copy

    def add_glow_effect(self, top, progress, progress_label, pyimage_copy):
        """
        RETURN THE A LIST OF SURFACES WITH THE ADDITIONAL EFFECT (GLOW) OR RETURN PYIMAGE_COPY UNCHANGED

        :param top: tkinter toplevel window; This window will be used for displaying the overall process
        :param progress: ttk progressbar; Bar showing the overall process
        :param progress_label: tkinter label showing the name of the effect, here glow effect
        :param pyimage_copy: Python list containing all the pygame surfaces to be processed
        :return: Return a list containing all the pygame surface post processing or unchanged if an error occur.
        """

        # SAVE THE SURFACE PRIOR GLOW
        pyimage_post_processing = pyimage_copy.copy()

        if self.gl.glow_checkbox.get() is True:

            surface = self.gl.glow_shape_pygame
            surface = hsv_surface24c(
                surface, (int(self.gl.glow_scale_value.get()) + 180) / 360.0).convert(24, pygame.RLEACCEL)
            ww, hh = surface.get_size()

            if self.gl.input_format_32bit.get():
                # print("Adding glow effect for 32-bit format image...")

                w, h = pyimage_copy[0].get_size()
                end = len(pyimage_copy)

                increment_x = (end - 1) / ((SCREEN.get_width() + 2 * ww) / ww)

                glow_surface = pygame.transform.smoothscale(surface, (ww, h))
                x = -ww
                for i in range(0, end):

                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='glow effect')
                        progress['value'] = i * 400 / end
                        progress.update()
                        top.update_idletasks()
                        surf = pyimage_copy[i].copy()
                        surf.blit(glow_surface, (x, 0), special_flags=pygame.BLEND_RGBA_ADD)
                        pyimage_copy[i] = surf
                        x += increment_x
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the glow process\nError: %s\n"
                                     "The glow effect will be disregarded" % error)

                        return pyimage_post_processing

            else:

                # print("Adding glow effect for 24-bit format image...")
                w, h = pyimage_copy[0].get_size()
                end = len(pyimage_copy)

                x = 0
                y = 0
                increment_x = 0
                increment_y = 0

                if self.gl.glow_direction.get() == "right":
                    x = -ww
                    y = 0
                    increment_x = (SCREEN.get_width() + ww) / end
                    glow_surface = pygame.transform.smoothscale(surface, (ww * 4, h))

                elif self.gl.glow_direction.get() == 'left':
                    x = SCREEN.get_width()
                    y = 0
                    glow_surface = pygame.transform.smoothscale(surface, (ww * 4, h))
                    increment_x = -((SCREEN.get_width() + ww * 4) / end)
                elif self.gl.glow_direction.get() == 'down':
                    x = 0
                    y = -hh * 4
                    glow_surface = pygame.transform.smoothscale(surface, (w, hh * 4))
                    increment_y = (SCREEN.get_height() + hh * 4) / end
                    increment_x = 0
                elif self.gl.glow_direction.get() == 'up':
                    x = 0
                    y = SCREEN.get_height()
                    glow_surface = pygame.transform.smoothscale(surface, (w, hh * 4))
                    increment_y = -((SCREEN.get_height() + hh * 4)  / end)
                    increment_x = 0
                elif self.gl.glow_direction.get() == 'top_l to bottom_r':
                    glow_surface = pygame.transform.smoothscale(surface, (w*2, h*2))
                    x = -w * 2
                    y = -h * 2
                    increment_x = ((SCREEN.get_width() + w * 2) / end)
                    increment_y = ((SCREEN.get_height() + h * 2) / end)
                    pass
                elif self.gl.glow_direction.get() == 'top_r to bottom_l':
                    glow_surface = pygame.transform.smoothscale(surface, (w*2, h*2))
                    x = SCREEN.get_width()
                    y = -h * 2
                    increment_x = -((SCREEN.get_width() + w * 2) / end)
                    increment_y = ((SCREEN.get_height() + h * 2) / end)
                    pass

                for i in range(0, end):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='glow effect')
                        progress['value'] = i * 400 / end
                        progress.update()
                        top.update_idletasks()
                        surf = pyimage_copy[i].copy()
                        surf.blit(glow_surface, (x, y), special_flags=pygame.BLEND_RGBA_ADD)
                        pyimage_copy[i] = surf
                        x += increment_x
                        y += increment_y

                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the glow process\nError: %s\n"
                                     "The glow effect will be disregarded" % error)
                        return pyimage_post_processing
        return pyimage_copy

    def add_channel_effect(self, top, progress, progress_label, pyimage_copy):
        """
        RETURN THE A LIST OF SURFACES WITH THE ADDITIONAL EFFECT (CHANNEL) OR RETURN PYIMAGE_COPY UNCHANGED

        :param top: tkinter toplevel window; This window will be used for displaying the overall process
        :param progress: ttk progressbar; Bar showing the overall process
        :param progress_label: tkinter label showing the name of the effect, here CHANNEL effect
        :param pyimage_copy: Python list containing all the pygame surfaces to be processed
        :return: Return a list containing all the pygame surface post processing or unchanged if an error occur.
        """

        # SAVE THE SURFACE PRIOR CHANNEL
        pyimage_post_processing = pyimage_copy.copy()

        if self.gl.channel_checkbox.get() is True:

            if self.gl.input_format_32bit.get():
                # print("Adding RGB channel effect for 32-bit format image...")
                for i in range(0, len(pyimage_copy)):

                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='channel effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()

                        # TODO CHECK THIS
                        pyimage_copy[i] = swap_channels32_c(pyimage_copy[i], self.channel_get_mode())
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the RGB channel process\nError: %s\n"
                                     "The RGB channel effect will be disregarded" % error)
                        return pyimage_post_processing

            else:

                # print("Adding RGB channel effect for 24-bit format image...")

                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='channel effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()
                        pyimage_copy[i] = swap_channels24_c(pyimage_copy[i], self.channel_get_mode())
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the RGB channel process\nError: %s\n"
                                     "The RGB channel effect will be disregarded" % error)
                        return pyimage_post_processing
        return pyimage_copy

    def add_rgbsplit_effect(self, top, progress, progress_label, pyimage_copy):
        """
        RETURN THE A LIST OF SURFACES WITH THE ADDITIONAL EFFECT (RGB SPLIT) OR RETURN PYIMAGE_COPY UNCHANGED

        :param top: tkinter toplevel window; This window will be used for displaying the overall process
        :param progress: ttk progressbar; Bar showing the overall process
        :param progress_label: tkinter label showing the name of the effect, here rgb split effect
        :param pyimage_copy: Python list containing all the pygame surfaces to be processed
        :return: Return a list containing all the pygame surface post processing or unchanged if an error occur.
        """

        # SAVE THE SURFACE PRIOR RGB SPLIT
        pyimage_post_processing = pyimage_copy.copy()

        if self.gl.rgbsplit_checkbox.get() is True:
            try:
                x_offset = int(self.gl.rgbsplitxoffset.get())
                if x_offset < 0:
                    x_offset = 0
                if x_offset > 50:
                    raise ValueError
            except:
                messagebox.showwarning(
                    "Error", "RGB split effect\nIncorrect x offset value\nExpecting value in range [0 ... 50]")
                return pyimage_post_processing

            try:
                y_offset = int(self.gl.rgbsplityoffset.get())
                if y_offset < 0:
                    y_offset = 0
                if y_offset > 50:
                    raise ValueError
            except:
                messagebox.showwarning(
                    "Error", "RGB split effect\nIncorrect y offset value\nExpecting value in range [0 ... 50]")
                return pyimage_post_processing

            try:
                start = int(self.gl.rgbsplit_start_frame.get())
            except:
                messagebox.showwarning("Error", "RGB split effect\nIncorrect start frame value")
                return pyimage_post_processing

            try:
                end = int(self.gl.rgbsplit_end_frame.get())
            except:
                messagebox.showwarning("Error", "RGB split effect\nIncorrect end frame value")
                return pyimage_post_processing

            if start > end:
                messagebox.showwarning("Error", "RGB split effect\nstart frame cannot be > end frame")
                return pyimage_post_processing

            if end < start:
                messagebox.showwarning("Error", "RGB split effect\nend frame cannot be < start frame")
                return pyimage_post_processing

            w, h = pyimage_copy[0].get_size()

            if self.gl.input_format_32bit.get():
                # print("Adding RGB split effect for 32-bit format image...")
                for i in range(start, end):

                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='rgb split effect')
                        progress['value'] = i * 400 / (end - start)
                        progress.update()
                        top.update_idletasks()
                        new_surface = pygame.Surface((w + 2 * x_offset, h + 2 * y_offset), pygame.SRCALPHA)
                        new_surface.fill((0, 0, 0, 0))
                        new_surface = new_surface.convert_alpha()
                        surf = new_surface.copy()
                        red_layer, green_layer, blue_layer = rgb_split_channels_alpha(pyimage_copy[i])
                        if self.gl.split_red_checkbox.get() == 1:
                            surf.blit(red_layer, (0, 0))  # , special_flags=pygame.BLEND_RGB_ADD)
                        if self.gl.split_green_checkbox.get() == 1:
                            surf.blit(green_layer, (x_offset, y_offset), special_flags=pygame.BLEND_RGB_ADD)
                        if self.gl.split_blue_checkbox.get() == 1:
                            surf.blit(blue_layer, (x_offset * 2, y_offset * 2), special_flags=pygame.BLEND_RGB_ADD)
                        pyimage_copy[i] = surf

                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the RGB split process\nError: %s\n"
                                     "The RGB split effect will be disregarded" % error)
                        return pyimage_post_processing

            else:

                #  print("Adding RGB split effect for 24-bit format image...")

                for i in range(start, end):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='rgb split effect')
                        progress['value'] = i * 400 / (end - start)
                        progress.update()
                        top.update_idletasks()
                        new_surface = pygame.Surface((w + 2 * x_offset, h + 2 * y_offset))
                        new_surface.fill((0, 0, 0, 0))
                        surf = new_surface.copy()
                        red_layer, green_layer, blue_layer = rgb_split_channels(pyimage_copy[i])
                        if self.gl.split_red_checkbox.get() == 1:
                            surf.blit(red_layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                        if self.gl.split_green_checkbox.get() == 1:
                            surf.blit(green_layer, (x_offset, y_offset), special_flags=pygame.BLEND_RGB_ADD)
                        if self.gl.split_blue_checkbox.get() == 1:
                            surf.blit(blue_layer, (x_offset * 2, y_offset * 2),
                                      special_flags=pygame.BLEND_RGB_ADD)
                        pyimage_copy[i] = surf
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the RGB split process\nError: %s\n"
                                     "The RGB split effect will be disregarded" % error)
                        return pyimage_post_processing
        return pyimage_copy

    def add_transition_effect(self, top, progress, progress_label, pyimage_copy):
        """
        RETURN THE A LIST OF SURFACES WITH THE ADDITIONAL EFFECT (TRANSITION) OR RETURN PYIMAGE_COPY UNCHANGED

        :param top: tkinter toplevel window; This window will be used for displaying the overall process
        :param progress: ttk progressbar; Bar showing the overall process
        :param progress_label: tkinter label showing the name of the effect, here transition effect
        :param pyimage_copy: Python list containing all the pygame surfaces to be processed
        :return: Return a list containing all the pygame surface post processing or unchanged if an error occur.
        """

        # SAVE THE SURFACE PRIOR TRANSITION EFFECT
        pyimage_post_processing = pyimage_copy.copy()

        if self.gl.transition_checkbox.get() is True:

            try:
                start = int(self.gl.transition_start_frame.get())
            except:
                messagebox.showwarning("Error", "Transition effect\nIncorrect start frame value")
                return pyimage_post_processing

            try:
                end = int(self.gl.transition_end_frame.get())
            except:
                messagebox.showwarning("Error", "Transition effect\nIncorrect end frame value")
                return pyimage_post_processing

            if start > end:
                messagebox.showwarning("Error", "Transition effect\nstart frame cannot be > end frame")
                return pyimage_post_processing

            if end < start:
                messagebox.showwarning("Error", "Transition effect\nend frame cannot be < start frame")
                return pyimage_post_processing

            if start < 0:
                start = 0
            if end > len(self.gl.pyimage):
                end = len(self.gl.pyimage)

            surface2 = self.gl.transition_texture
            w, h = pyimage_copy[0].get_size()
            surface2 = pygame.transform.smoothscale(surface2, (w, h))

            if self.gl.input_format_32bit.get():
                # print("Adding transition effect for 32-bit format image...")
                for i in range(start, end):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='transition effect')
                        progress['value'] = i * 400 / (end - start)
                        progress.update()
                        top.update_idletasks()
                        pyimage_copy[i] = blend_to_textures_32c(pyimage_copy[i], surface2, (100 / end) * i)

                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the transition process\nError: %s\n"
                                     "The transition effect will be disregarded" % error)
                        return pyimage_post_processing
            else:

                # print("Adding transition effect for 24-bit format image...")

                for i in range(start, end):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")
                        progress_label.configure(text='transition effect')
                        progress['value'] = i * 400 / (end - start)
                        progress.update()
                        top.update_idletasks()
                        pyimage_copy[i] = blend_to_textures_24c(pyimage_copy[i], surface2, (100.0 / end) * i)

                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the transition process\nError: %s\n"
                                     "The transition effect will be disregarded" % error)
                        return pyimage_post_processing

        return pyimage_copy

    def add_glitch_effect(self, top, progress, progress_label, pyimage_copy):
        """
        RETURN THE A LIST OF SURFACES WITH THE ADDITIONAL EFFECT (GLITCH) OR RETURN PYIMAGE_COPY UNCHANGED

        :param top: tkinter toplevel window; This window will be used for displaying the overall process
        :param progress: ttk progressbar; Bar showing the overall process
        :param progress_label: tkinter label showing the name of the effect, here glitch effect
        :param pyimage_copy: Python list containing all the pygame surfaces to be processed
        :return: Return a list containing all the pygame surface post processing or unchanged if an error occur.
        """

        # SAVE THE SURFACE PRIOR GLITCH EFFECT
        pyimage_post_processing = pyimage_copy.copy()

        if self.gl.glitch_checkbox.get() is True:

            try:
                start = int(self.gl.glitch_start_frame.get())
            except:
                messagebox.showwarning("Error", "Glitch effect\nIncorrect start frame value")
                return pyimage_post_processing

            try:
                end = int(self.gl.glitch_end_frame.get())
            except:
                messagebox.showwarning("Error", "Glitch effect\nIncorrect end frame value")
                return pyimage_post_processing

            if start > end:
                messagebox.showwarning("Error", "Glitch effect\nstart frame cannot be > end frame")
                return pyimage_post_processing

            if end < start:
                messagebox.showwarning("Error", "Glitch effect\nend frame cannot be < start frame")
                return pyimage_post_processing

            if start < 0:
                start = 0
            if end > len(self.gl.pyimage):
                end = len(self.gl.pyimage)

            if self.gl.glitch_horizontal.get():

                if self.gl.input_format_32bit.get():
                    # print("Adding glitch effect for 32-bit format image...")
                    for i in range(start, end):

                        try:
                            if self.gl.cancel:
                                raise Exception("Process aborted by user")

                            progress_label.configure(text='glitch effect')
                            progress['value'] = i * 400 / (end - start)
                            progress.update()
                            top.update_idletasks()
                            pyimage_copy[i] = horizontal_glitch32(
                                pyimage_copy[i].convert_alpha(), 1, 0.1, 10)

                        except Exception as error:
                            messagebox.showerror(
                                "Error", "An error occurred during the glitch process\nError: %s\n"
                                         "The glitch effect will be disregarded" % error)
                            return pyimage_post_processing
                else:

                    # print("Adding glitch effect for 24-bit format image...")

                    for i in range(start, end):
                        try:
                            if self.gl.cancel:
                                raise Exception("Process aborted by user")

                            progress_label.configure(text='glitch effect')
                            progress['value'] = i * 400 / (end - start)
                            progress.update()
                            top.update_idletasks()
                            pyimage_copy[i] = horizontal_glitch24(pyimage_copy[i].convert(),
                                                                  1, 0.3, (50 + (360 / 30) * i) % 20)

                        except Exception as error:
                            messagebox.showerror(
                                "Error", "An error occurred during the glitch process\n Error: %s\n"
                                         "The glitch effect will be disregarded" % error)
                            return pyimage_post_processing

            if self.gl.glitch_vertical.get():

                if self.gl.input_format_32bit.get():
                    # print("Adding glitch effect for 32-bit format image...")
                    for i in range(start, end):

                        try:
                            if self.gl.cancel:
                                raise Exception("Process aborted by user")

                            progress_label.configure(text='glitch effect')
                            progress['value'] = i * 400 / (end - start)
                            progress.update()
                            top.update_idletasks()
                            pyimage_copy[i] = vertical_glitch32_c(
                                pyimage_copy[i].convert_alpha(), 1, 0.1, 10).convert_alpha()

                        except Exception as error:
                            messagebox.showerror(
                                "Error", "An error occurred during the glitch process\nError: %s\n"
                                         "The glitch effect will be disregarded" % error)
                            return pyimage_post_processing
                else:

                    # print("Adding glitch effect for 24-bit format image...")

                    for i in range(start, end):
                        try:
                            if self.gl.cancel:
                                raise Exception("Process aborted by user")

                            progress_label.configure(text='glitch effect')
                            progress['value'] = i * 400 / (end - start)
                            progress.update()
                            top.update_idletasks()
                            pyimage_copy[i] = vertical_glitch24_c(pyimage_copy[i].convert(),
                                                                  1, 0.3, (50 + (360 / 30) * i) % 20)

                        except Exception as error:
                            messagebox.showerror(
                                "Error", "An error occurred during the glitch process\nError: %s\n"
                                         "The glitch effect will be disregarded" % error)
                            return pyimage_post_processing

        return pyimage_copy

    def add_sepia_effect(self, top, progress, progress_label, pyimage_copy):

        # SAVE THE SURFACE PRIOR GLITCH EFFECT
        pyimage_post_processing = pyimage_copy.copy()
        if bool(self.gl.sepia.get()):

            if bool(self.gl.input_format_32bit.get()):
                # print("Adding sepia effect for 32-bit format image...")
                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='sepia effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()

                        pyimage_copy[i] = sepia24_c(pyimage_copy[i])
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the sepia process\nError: %s\n"
                                     "The sepia effect will be disregarded" % error)
                        return pyimage_post_processing

            elif bool(self.gl.input_format_24bit.get()):

                # Adding sepia effect for 24-bit format image...")
                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='sepia effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()

                        pyimage_copy[i] = sepia24_c(pyimage_copy[i])

                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the sepia process\nError: %s\n"
                                     "The sepia effect will be disregarded" % error)
                        return pyimage_post_processing

        return pyimage_copy

    def add_greyscale_effect(self, top, progress, progress_label, pyimage_copy):
        # SAVE THE SURFACE PRIOR GLITCH EFFECT
        pyimage_post_processing = pyimage_copy.copy()

        if bool(self.gl.greyscale.get()):

            if bool(self.gl.input_format_32bit.get()):
                # print("Adding greyscale effect for 32-bit format image...")
                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='greyscale effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()

                        pyimage_copy[i] = greyscale32_c(pyimage_copy[i])

                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the greyscale process\nError: %s\n"
                                     "The greyscale effect will be disregarded" % error)
                        return pyimage_post_processing

            elif bool(self.gl.input_format_24bit.get()):

                # print("Adding greyscale effect for 24-bit format image...")
                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='greyscale effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()

                        pyimage_copy[i] = greyscale24_c(pyimage_copy[i])

                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the greyscale process\nError: %s\n"
                                     "The greyscale effect will be disregarded" % error)
                        return pyimage_post_processing

        return pyimage_copy

    def add_pixelated_effect(self, top, progress, progress_label, pyimage_copy):

        # SAVE THE SURFACE PRIOR GLITCH EFFECT
        pyimage_post_processing = pyimage_copy.copy()

        w, h = pyimage_copy[0].get_size()

        try:
            px_block = self.gl.pixel_size.get()
            if px_block < 4:
                raise ValueError
            if px_block not in [4, 8, 16, 32]:
                raise ValueError
        except:
            messagebox.showwarning("Error", "pixel effect\nIncorrect pixel block size value\n"
                                            " The value must be either [4, 8, 16, 32]")
            return pyimage_post_processing

        if bool(self.gl.pixel.get()):

            if bool(self.gl.input_format_32bit.get()):
                # print("Adding pixelate effect for 32-bit format image...")
                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='pixelate effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()

                        subs = create_pixel_blocks_rgba(pyimage_copy[i], px_block, int(w / px_block), int(h / px_block))

                        ii = 0
                        for surface in subs:
                            # avg=pygame.transform.average_color(surface)
                            # surface.fill(avg)
                            subs[ii] = pixelate32(surface)
                            ii += 1

                        new_surface = pygame.Surface((w, w)).convert_alpha()
                        new_surface.fill((0, 0, 0, 0))

                        # RECONSTRUCTION (ASSEMBLING ALL THE PIXELATED BLOCKS
                        ii = 0
                        jj = 0
                        for pixel_block in subs:

                            new_surface.blit(pixel_block, (ii, jj))
                            ii += px_block
                            if ii >= w:
                                jj += px_block
                                ii = 0

                        pyimage_copy[i] = new_surface.convert_alpha()

                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the pixelate process\nError: %s\n"
                                     "The pixelate effect will be disregarded" % error)
                        return pyimage_post_processing

            elif bool(self.gl.input_format_24bit.get()):

                # print("Adding pixelate effect for 24-bit format image...")
                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='pixelate effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()
                        subs = create_pixel_blocks_rgb(pyimage_copy[i], px_block, int(w/px_block), int(h/px_block))
                        ii = 0
                        for surface in subs:
                            subs[ii] = pixelate24(surface)
                            ii += 1

                        new_surface = pygame.Surface((w, w))
                        new_surface.fill((0, 0, 0))

                        ii = 0
                        jj = 0
                        for pixel_block in subs:

                            new_surface.blit(pixel_block, (ii, jj))
                            ii += px_block
                            if ii >= w:
                                jj += px_block
                                ii = 0

                        pyimage_copy[i] = new_surface.convert()

                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the pixelate process\nError: %s\n"
                                     "The pixelate effect will be disregarded" % error)
                        return pyimage_post_processing

        return pyimage_copy

    def add_dithering_effect(self, top, progress, progress_label, pyimage_copy):
        # SAVE THE SURFACE PRIOR GLITCH EFFECT
        pyimage_post_processing = pyimage_copy.copy()

        if bool(self.gl.dithering.get()):

            try:
                v = self.gl.dithering_value.get()
                if v < 0:
                    raise ValueError
            except:
                messagebox.showerror(
                    "Error", "Dithering effect\n"
                    "Incorrect reduction value, please choose\n"
                    "a value between 2^0 to 2^16 value range [0 ... 16]")
                return pyimage_post_processing

            if bool(self.gl.input_format_32bit.get()):
                # Adding dithering effect for 32-bit format image...")
                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='dithering effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()
                        pyimage_copy[i] = dithering32_c(pyimage_copy[i], v)
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the dithering process\nError: %s\n"
                                     "The dithering effect will be disregarded" % error)
                        return pyimage_post_processing

            elif bool(self.gl.input_format_24bit.get()):

                # print("Adding dithering effect for 24-bit format image...")
                for i in range(0, len(pyimage_copy)):
                    try:
                        if self.gl.cancel:
                            raise Exception("Process aborted by user")

                        progress_label.configure(text='dithering effect')
                        progress['value'] = i * 400 / len(pyimage_copy)
                        progress.update()
                        top.update_idletasks()
                        pyimage_copy[i] = dithering24_c(pyimage_copy[i], v)
                    except Exception as error:
                        messagebox.showerror(
                            "Error", "An error occurred during the dithering process\nError: %s\n"
                                     "The dithering effect will be disregarded" % error)
                        return pyimage_post_processing

        return pyimage_copy

    def preview(self, timing_=60) -> None:
        """

        :param timing_: integer; fps value, default 60 frames per seconds
        :return: None
        """

        self.preview_button.config(state="disabled")

        global BUFFER_TKINTER_OPTIONS

        preview = False

        if isinstance(BUFFER_TKINTER_OPTIONS, dict) and len(BUFFER_TKINTER_OPTIONS) != 0:
            buffer_keys = BUFFER_TKINTER_OPTIONS.keys()
            # buffer_values = BUFFER.values()
            # COMPARE BOTH DICTIONARIES
            for i, j in self.gl.__dict__.items():

                # COMPARE ONLY THE TKINTER VARIABLES
                if type(j) in (BooleanVar, IntVar, DoubleVar) or type(j).__name__ == "Combobox":
                    try:
                        v = j.get()
                        if i in buffer_keys:
                            if BUFFER_TKINTER_OPTIONS[i] != v:
                                preview = True
                    except:
                        pass

        else:
            # FIRST PREVIEW
            preview = True

        if not preview:
            i = 0
            a = set()
            b = set()
            for child in self.root.winfo_children():
                a.add(child)

            # todo check if the sprite list is null ?
            for surf in self.pyimage_copy:
                self.animation_canvas.delete('all')
                self.update_canvas(self.gl.tkimage[i % len(self.gl.tkimage)])
                self.refresh(surf)
                pygame.time.delay(int((1 / timing_ if timing_ != 0 else 0.016) * 1000))
                i += 1
            for child in self.root.winfo_children():
                b.add(child)
            c = b.difference(a)
            for obj in c:
                obj.destroy()
            self.preview_button.config(state="normal")
            return

        self.pyimage_copy = self.gl.pyimage.copy()

        def cancel_preview():
            if top.winfo_exists():
                top.destroy()
            self.gl.cancel = True
            return

        self.preview_button.config(state="disabled")
        self.preview_button.update()

        if preview:

            for i, j in self.gl.__dict__.items():
                # COMPARE ONLY THE TKINTER VARIABLES
                if type(j) in (BooleanVar, IntVar, DoubleVar) or type(j).__name__ == "Combobox":
                    # UPDATE DICTIONARY
                    try:
                        v = j.get()
                        BUFFER_TKINTER_OPTIONS[i] = v
                    except:
                        pass

            # PROCESSING SPRITESHEET ONLY IF THE SPRITE ANIMATION IS NOT NULL
            if isinstance(self.gl.pyimage, list):
                if len(self.gl.pyimage) == 0:
                    messagebox.showinfo("Info", "Please load a spritesheet first\nSection input settings option Load")
                else:

                    top = tkinter.Toplevel(self.root, bg="#858585", bd=2, height=150, width=500)
                    top.title("Processing")
                    top.update()
                    progress_label = Label(top, text="Current process : ", bg="#858585", fg="#ffffff",
                                           font=tkFont.Font(family='Helvetica', size=12, weight='normal'))
                    progress_label.grid(row=1, column=1, pady=5)
                    top.update_idletasks()
                    top.update()
                    progress = ttk.Progressbar(top, orient=HORIZONTAL, length=400, mode='determinate')
                    progress.grid(row=2, column=1, pady=5)
                    progress.update()
                    progress['value'] = 0
                    self.gl.cancel = False
                    cancel = Button(top, text="Cancel", bg="#858585", fg="#ffffff", command=cancel_preview, width=10)
                    cancel.grid(row=3, column=1, pady=10)
                    # todo remove self.pyimage_copy from the argument
                    # BLENDING EFFECT
                    self.pyimage_copy = self.add_blend_effect(top, progress, progress_label, self.pyimage_copy)
                    # HSV EFFECT
                    self.pyimage_copy = self.add_hsv_effect(top, progress, progress_label, self.pyimage_copy)
                    # BLOOM EFFECT
                    self.pyimage_copy = self.add_bloom_effect(top, progress, progress_label, self.pyimage_copy)
                    # SATURATION EFFECT
                    self.pyimage_copy = self.add_saturation_effect(top, progress, progress_label, self.pyimage_copy)
                    # CARTOON EFFECT
                    self.pyimage_copy = self.add_cartoon_effect(top, progress, progress_label, self.pyimage_copy)
                    # BLUR EFFECT
                    self.pyimage_copy = self.add_blur_effect(top, progress, progress_label, self.pyimage_copy)
                    # GLOW EFFECT
                    self.pyimage_copy = self.add_glow_effect(top, progress, progress_label, self.pyimage_copy)
                    # CHANNEL EFFECT
                    self.pyimage_copy = self.add_channel_effect(top, progress, progress_label, self.pyimage_copy)
                    # RGB SPLIT EFFECT
                    self.pyimage_copy = self.add_rgbsplit_effect(top, progress, progress_label, self.pyimage_copy)
                    # TRANSITION EFFECT
                    self.pyimage_copy = self.add_transition_effect(top, progress, progress_label, self.pyimage_copy)
                    # GLITCH EFFECT
                    self.pyimage_copy = self.add_glitch_effect(top, progress, progress_label, self.pyimage_copy)
                    # DITHERING
                    self.pyimage_copy = self.add_dithering_effect(top, progress, progress_label, self.pyimage_copy)
                    # PIXELATED
                    self.pyimage_copy = self.add_pixelated_effect(top, progress, progress_label, self.pyimage_copy)
                    # SEPIA
                    self.pyimage_copy = self.add_sepia_effect(top, progress, progress_label, self.pyimage_copy)
                    # GREYSCALE
                    self.pyimage_copy = self.add_greyscale_effect(top, progress, progress_label, self.pyimage_copy)

                    # todo ERROR handling
                    if len(self.pyimage_copy) != 0:
                        for j in range(len(self.pyimage_copy)):
                            if self.gl.inverse_variable.get() == 1:
                                if self.gl.input_format_24bit.get():
                                    if self.gl.inverse_exclude_variable.get():
                                        self.pyimage_copy[j] = invert_surface_24bit_exclude(
                                            self.pyimage_copy[j], self.gl.exclude_red_inv.get(),
                                            self.gl.exclude_green_inv.get(),
                                            self.gl.exclude_red_inv.get())
                                    else:
                                        self.pyimage_copy[j] = invert_surface_24bit(self.pyimage_copy[j])
                                else:
                                    if self.gl.inverse_exclude_variable.get():

                                        self.pyimage_copy[j] = invert_surface_32bit_exclude(
                                            self.pyimage_copy[j], self.gl.exclude_red_inv.get(),
                                            self.gl.exclude_green_inv.get(),
                                            self.gl.exclude_red_inv.get())
                                    else:
                                        self.pyimage_copy[j] = invert_surface_32bit(self.pyimage_copy[j])

                    if len(self.pyimage_copy) == 0:
                        self.pyimage_copy = self.gl.pyimage

                    self.animation_canvas.delete('all')

                    self.gl.tkimage = []

                    if self.gl.input_format_24bit.get():
                        # BUILD THE TKINTER CANVAS ANIMATION
                        for surf in self.pyimage_copy:
                            surf = pygame.transform.smoothscale(surf, (256, 256))
                            image_str = pygame.image.tostring(surf, 'RGB')  # use 'RGB' to export
                            w, h = surf.get_rect()[2:]
                            image = Image.frombytes('RGB', (w, h), image_str)
                            tk_image = ImageTk.PhotoImage(image)  # use ImageTk.PhotoImage class instead
                            self.gl.tkimage.append(tk_image)
                    else:
                        for surf in self.pyimage_copy:
                            surf = pygame.transform.smoothscale(surf, (256, 256))
                            image_str = pygame.image.tostring(surf, 'RGBA')
                            w, h = surf.get_rect()[2:]
                            image = Image.frombytes('RGBA', (w, h), image_str)
                            tk_image = ImageTk.PhotoImage(image)  # use ImageTk.PhotoImage class instead
                            self.gl.tkimage.append(tk_image)

                    a = set()
                    b = set()
                    for child in self.root.winfo_children():
                        a.add(child)
                    i = 0
                    for surf in self.pyimage_copy:
                        self.animation_canvas.delete('all')
                        self.update_canvas(self.gl.tkimage[i % len(self.pyimage_copy)])
                        self.refresh(surf)
                        pygame.time.delay(int((1 / timing_ if timing_ != 0 else 16) * 1000))
                        i += 1
                    for child in self.root.winfo_children():
                        b.add(child)
                    c = b.difference(a)
                    for obj in c:
                        obj.destroy()

                    self.preview_button.config(state="normal")
                    top.update()
                    top.destroy()
            else:
                messagebox.showerror(
                    "Error", "Expecting a list type for the preview buffer, got %s" % type(self.gl.pyimage))
                self.preview_button.config(state="normal")
                return
        self.preview_button.config(state="normal")
        self.preview_button.update()


pygame.display.set_caption("Preview animation")

print('Driver          : ', pygame.display.get_driver())
print(pygame.display.Info())
# New in pygame 1.9.5.
try:
    print('Display(s)      : ', pygame.display.get_num_displays())
except AttributeError:
    pass
sdl_version = pygame.get_sdl_version()
print('SDL version     : ', sdl_version)
print('Pygame version  : ', pygame.version.ver)
python_version = sys.version_info
print('Python version  :  %s.%s.%s ' % (python_version[0], python_version[1], python_version[2]))
print('Platform        : ', platform.version())
# print('Available modes : ', pygame.display.list_modes())

root = tkinter.Tk()
root.configure(background="DARKGRAY")
root.iconbitmap('Assets\\magma.ico')
gl = GL()

SpriteSheetStudio(root, gl)

root.update()
root.deiconify()
root.after(200, root.attributes, "-alpha", 1.0)
root.configure(background='DARKGRAY')
root.mainloop()

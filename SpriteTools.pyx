
#cython: boundscheck=False, wraparound=False, nonecheck=False, cdivision=True, optimize.use_switch=True
# encoding: utf-8


# todo explain inplace (different approach)

from __future__ import print_function


import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=ImportWarning)

# NUMPY IS REQUIRED
try:
    import numpy
    from numpy import ndarray, zeros, empty, uint8, int32, float64, float32, dstack, full, ones,\
    asarray, ascontiguousarray, full_like, add, putmask, int16, arange, repeat, newaxis
except ImportError:
    print("\n<numpy> library is missing on your system."
          "\nTry: \n   C:\\pip install numpy on a window command prompt.")
    raise SystemExit

cimport numpy as np

try:
    cimport cython
    from cython.parallel cimport prange
    from cpython cimport PyObject_CallFunctionObjArgs, PyObject, \
        PyList_SetSlice, PyObject_HasAttr, PyObject_IsInstance, \
        PyObject_CallMethod, PyObject_CallObject
    from cpython.dict cimport PyDict_DelItem, PyDict_Clear, PyDict_GetItem, PyDict_SetItem, \
        PyDict_Values, PyDict_Keys, PyDict_Items
    from cpython.list cimport PyList_Append, PyList_GetItem, PyList_Size, PyList_SetItem
    from cpython.object cimport PyObject_SetAttr

except ImportError:
    raise ImportError("\n<cython> library is missing on your system."
          "\nTry: \n   C:\\pip install cython on a window command prompt.")

try:
    import pygame
    from pygame import Rect
    from pygame.math import Vector2
    from pygame import Rect, BLEND_RGB_ADD, HWACCEL
    from pygame import Surface, SRCALPHA, mask, RLEACCEL
    from pygame.transform import rotate, scale, smoothscale
    from pygame.surfarray import array3d, pixels3d, array_alpha, pixels_alpha
    from pygame.image import frombuffer

except ImportError:
    raise ImportError("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")

from libc.math cimport sqrt, atan2, sin, cos, exp, round
from libc.stdlib cimport srand, rand, malloc, free
from libc.stdio cimport printf

DEF M_PI = 3.14159265359


cdef extern from 'randnumber.c':
    void init_clock()nogil;
    float randRangeFloat(float lower, float upper)nogil;
    int randRange(int lower, int upper)nogil;

cdef extern from "library.c":
    int *quickSort(int arr[], int low, int high)nogil;
    unsigned char max_rgb_value(unsigned char red, unsigned char green, unsigned char blue)nogil;
    unsigned char min_rgb_value(unsigned char red, unsigned char green, unsigned char blue)nogil;


DEF SCHEDULE = 'static'

DEF OPENMP = True
# num_threads – The num_threads argument indicates how many threads the team should consist of.
# If not given, OpenMP will decide how many threads to use.
# Typically this is the number of cores available on the machine. However,
# this may be controlled through the omp_set_num_threads() function,
# or through the OMP_NUM_THREADS environment variable.
DEF THREAD_NUMBER = 1
if OPENMP is True:
    DEF THREAD_NUMBER = 8

# Deprecated
cpdef blend_texture_32(object surface_, float interval_, tuple color_):
    """
    BLEND A 32-BIT TEXTURE WITH A GIVEN COLOR (RGB)
    
    * Deprecated blend_texture_32c is a faster version 
    * Video mode must be initialised otherwise an error message will be raised
    * Create a new surface
    * non optimize version of blend texture
    * Compatible only with 32 bit image with transparency, an error will be raised if 
      the surface is 24-bit or 8-bit 
    * Image returned is 32-bit with transparency converted for fast blit (convert_alpha)
    * The Transparency layer will not be affected by the blending process 

    :param surface_: pygame.Surface to blend
    :param interval_: float; value between [0.0 ... 1.0]. Zero no blending effect and 1.0 the output 
    surface is equivalent to surface_.fill(color_). Over 1.0 create saturation effect.
    :param color_: tuple rgb or rgba, only the first 3 values will be used (rgb colors).ex (255, 0, 0)
    :return: a 32-bit pygame Surface with transparency (original image blended with a given color) 
    """
    warnings.warn("Deprecated version, use blend_texture_32c instead", DeprecationWarning)
    # get rgb pixels
    cdef np.ndarray[np.uint8_t, ndim=3] source_array = pixels3d(surface_)
    # get alpha values
    cdef np.ndarray[np.uint8_t, ndim=2] alpha_channel = pixels_alpha(surface_)
    cdef np.ndarray[np.uint8_t, ndim=3] diff = \
        ((full_like(asarray(source_array).shape, color_[:3]) - asarray(source_array)) * interval_).astype(uint8)
    cdef np.ndarray[np.uint8_t, ndim=3] rgba_array = \
        dstack((add(source_array, diff), alpha_channel)).astype(dtype=numpy.uint8)
    return pygame.image.frombuffer((rgba_array.transpose(1, 0, 2)).tobytes(),
                                          (rgba_array.shape[0], rgba_array.shape[1]), 'RGBA').convert_alpha()


cpdef blend_texture_24(object surface_, float interval_, tuple color_):
    """
    BLEND A 24-BIT TEXTURE WITH A GIVEN COLOR (RGB)

    * Video mode must be initialised otherwise an error message will be raised
    * Create a new surface
    * non optimize version of blend texture
    * Compatible only with 24-bit image no transparency, an error will be raised if 
      the surface is 8-bit 
    * Image returned is 24-bit without transparency and fast blit (convert)
    * Blending a 24-bit image will also blend the transparency layer (background image color).
      If you do not want the background color to be blended use blend_texture_24_alpha instead
      

    :param surface_: pygame.Surface to blend
    :param interval_: float; value between [0.0 ... 1.0]. Zero no blending effect and 1.0 the output 
    surface is equivalent to surface_.fill(color_). Over 1.0 create saturation effect.
    :param color_: tuple rgb or rgba only the first 3 values will be used (rgb colors). ex (255, 0, 0)
    :return: a 24-bit pygame Surface without transparency (original image blended with a given color) 
    """
    # get rgb pixels
    cdef np.ndarray[np.uint8_t, ndim=3] source_array = pixels3d(surface_)
    cdef np.ndarray[np.uint8_t, ndim=3] diff = \
        ((full_like(asarray(source_array).shape, color_[:3]) - asarray(source_array)) * interval_).astype(uint8)
    cdef np.ndarray[np.uint8_t, ndim=3] rgb_array  = add(source_array, diff).astype(dtype=numpy.uint8)
    return pygame.surfarray.make_surface(rgb_array).convert()


cpdef blend_texture_24_alpha(object surface_, float interval_, tuple color_, tuple background_color_=(0, 0, 0)):
    """
    BLEND A 24-BIT TEXTURE WITH A GIVEN COLOR (RGB). 
    SPECIFY A COLOR WITH background_color_ THAT WILL NOT BE MODIFIED DURING THE 
    BLENDING PROCESS (EX BACKGROUND COLOR)

    * Video mode must be initialised otherwise an error message will be raised
    * Create a new surface
    * non optimize version of blend texture
    * Compatible only with 24-bit image no transparency, an error will be raised if 
      the surface is 8-bit 
    * Image returned is 24-bit without transparency and fast blit (convert) 
      THIS IS NOT AN INPLACE OPERATION, a new surface is created and returned
        
    * Allow you to select a specific color that will not be blended during the process 
      ex background color.

    :param surface_  : pygame.Surface to blend
    :param interval_ : float; value between [0.0 ... 1.0]. Zero no blending effect and 1.0 the output 
    surface is equivalent to surface_.fill(color_). Over 1.0 create saturation effect.
    :param color_    : tuple rgb or rgba only the first 3 values will be used (rgb colors). ex (255, 0, 0)
    :param background_color_ : Background color that will not be modified during the blending process  
    :return: a 24-bit pygame Surface without transparency (original image blended with a given color) 
    """
    # get rgb pixels
    cdef np.ndarray[np.uint8_t, ndim=3] source_array = pixels3d(surface_)
    # mask for the background color
    mask = (source_array == background_color_[:3])
    cdef np.ndarray[np.uint8_t, ndim=3] diff = \
        ((full_like(asarray(source_array).shape, color_[:3]) - asarray(source_array)) * interval_).astype(uint8)
    cdef np.ndarray[np.uint8_t, ndim=3] rgb_array = add(source_array, diff).astype(dtype=numpy.uint8)
    rgb_array[numpy.where((mask == [True, True, True]).all(axis=2))] = [*background_color_]
    return pygame.surfarray.make_surface(rgb_array).convert()


cpdef blend_texture_24_alpha_inplace(
        object surface_, float percentage, tuple color_, tuple background_color_=(0, 0, 0)):


    if PyObject_IsInstance(color_, pygame.Color):
        color_ = (color_.r, color_.g, color_.b)

    elif PyObject_IsInstance(color_, (tuple, list)):
        assert len(color_)==3, \
            'Invalid color format, use format (R, G, B) or [R, G, B].'
        pass
    else:
        raise TypeError('Color type argument error.')

    assert PyObject_IsInstance(surface_, Surface), \
        'Argument surface_ must be a Surface got %s ' % type(surface_)

    assert 0.0 <= percentage <=100.0, \
        "Incorrect value for argument percentage should be [0.0 ... 100.0] got %s " % percentage

    if percentage == 0.0:
        return surface_

    cdef unsigned char[:, :, :] source_array
    try:
        source_array = pixels3d(surface_)
    except Exception as e:
        raise ValueError("Cannot reference pixels into a 3d array.\n %s " % e)

    cdef:
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        unsigned char [:] f_color = numpy.array(color_[:3], dtype=uint8)  # take only rgb values
        unsigned char [:] bc = numpy.array(background_color_, dtype=uint8)
        int c1, c2, c3
        float c4 = 1.0 / 100.0
        int i=0, j=0
        unsigned char r, g, b

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r, g, b =  source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2]

                if r!=bc[0] and g!=bc[1] and b!=bc[2]:

                    c1 = min(<int> (r + ((f_color[0] - r) * c4) * percentage), 255)
                    c2 = min(<int> (g + ((f_color[1] - g) * c4) * percentage), 255)
                    c3 = min(<int> (b + ((f_color[2] - b) * c4) * percentage), 255)
                    if c1 < 0:
                        c1 = 0
                    if c2 < 0:
                        c2 = 0
                    if c3 < 0:
                        c3 = 0

                    source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2] = c1, c2, c3


cpdef blend_texture_24_alpha_threshold_inplace(object surface_, float percentage, tuple color_, unsigned int tresh_):
    """
    
    :param surface_: Pygame surface to blend 
    :param percentage: float must be in range (0.0 ... 100.0)
    :param color_: tuple; The surface will be blend with color_
    :param tresh_: integer; Threshold, (r + g + b) > tresh_ the pixel will be blended with the given
    color otherwise the pixel will remain unchanged
    :return: 
    """

    if PyObject_IsInstance(color_, pygame.Color):
        color_ = (color_.r, color_.g, color_.b)

    elif PyObject_IsInstance(color_, (tuple, list)):
        assert len(color_)==3, \
            'Invalid color format, use format (R, G, B) or [R, G, B].'
        pass
    else:
        raise TypeError('Color type argument error.')

    assert PyObject_IsInstance(surface_, Surface), \
        'Argument surface_ must be a Surface got %s ' % type(surface_)

    assert 0.0 <= percentage <=100.0, \
        "Incorrect value for argument percentage should be [0.0 ... 100.0] got %s " % percentage

    if percentage == 0.0:
        return surface_

    cdef unsigned char[:, :, :] source_array
    try:
        source_array = pixels3d(surface_)
    except Exception as e:
        raise ValueError("Cannot reference pixels into a 3d array.\n %s " % e)

    cdef:
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        unsigned char [:] f_color = numpy.array(color_[:3], dtype=uint8)  # take only rgb values
        int c1, c2, c3
        float c4 = 1.0 / 100.0
        int i=0, j=0
        unsigned char r, g, b

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r, g, b =  source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2]

                if (r + g + b) > tresh_:

                    c1 = min(<int> (r + ((f_color[0] - r) * c4) * percentage), 255)
                    c2 = min(<int> (g + ((f_color[1] - g) * c4) * percentage), 255)
                    c3 = min(<int> (b + ((f_color[2] - b) * c4) * percentage), 255)
                    if c1 < 0:
                        c1 = 0
                    if c2 < 0:
                        c2 = 0
                    if c3 < 0:
                        c3 = 0

                    source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2] = c1, c2, c3


# Deprecated
cpdef add_transparency_all(np.ndarray[np.uint8_t, ndim=3] rgb_array_,
                           np.ndarray[np.uint8_t, ndim=2] alpha_array, int alpha_to_subtract):
    """
    GIVEN TWO ARRAYS RGB & ALPHA, MODIFY ALPHA VALUES AND BUILD A NEW SURFACE FROM BOTH ARRAYS
    
    * Subtract array alpha values with new alpha value (value_). When alpha_to_subtract = 0, the output
      surface remains unchanged (equivalent stack of RGB & alpha). When alpha_to_subtract = 255, The 
      surface is 100% transparent.
    * Create a new surface
    * Return a pygame.Surface 32-bit with transparency converted for fast blit (convert_alpha())
    * Argument value_ cannot be < 0
    * Output Surface is already converted with convert_alpha()
    
    :param rgb_array_: numpy.ndarray; 3d array uint8 with RGB values type(w, h, 3)
    :param alpha_array    : numpy.ndarray; 2d array uint8 with alpha values type (w, h)
    :param alpha_to_subtract : integer; Cannot be < 0, range [0, 255] 
    :return: Return a pygame.Surface 32-bit with transparency converted for fast blit (convert_alpha())
    """
    warnings.warn("Deprecated version, use make_transparent32 or make_transparent32_inplace instead", DeprecationWarning)

    if alpha_to_subtract < 0 or alpha_to_subtract> 255:
        raise ValueError('Argument value_ must be in range [0 ... 255], got %s' % alpha_to_subtract)

    # transform the array into int16 (allow alpha values to be < 0)
    alpha = alpha_array.astype(int16)
    alpha -= alpha_to_subtract
    putmask(alpha, alpha < 0, 0)
    return make_surface(make_array(rgb_array_, alpha.astype(numpy.uint8))).convert_alpha()


cpdef float damped_oscillation(double t)nogil:
    return <float>(exp(-t/10) * cos(M_PI * t))


cpdef make_array_cython(unsigned char[:, :, :] rgb_array_c, unsigned char[:, :] alpha_c):
    """
    STACK ARRAY RGB VALUES WITH ALPHA CHANNEL.
    CREATE A 3D ARRAY CONTAINING RGBA VALUES SIMILAR TO NUMPY.DSTACK 
    
    * Use this version if rgb_array and alpha_array are memoryviewslice 
    * Return a new array type ndarray (w, h, 4) type unsigned char (uint8)
    
    :param rgb_array_c: numpy.ndarray (w, h, 3) uint8 containing RGB values 
    :param alpha_c    : numpy.ndarray (w, h) uint8 containing alpha values 
    :return           : return a numpy.ndarray (w, h, 4) uint8, stack array of RGBA values
    The values are copied into a new array (out array is not transpose).
    """

    cdef int width, height
    try:
        width, height = (<object> rgb_array_c).shape[:2]
    except (ValueError, pygame.error) as e:
        raise ValueError('Array shape not understood.')

    cdef:
        unsigned char[:, :, ::1] new_array =  empty((width, height, 4), dtype=uint8)
        int i=0, j=0
    # EQUIVALENT TO A NUMPY DSTACK
    # USE MULTI-PROCESSING
    with nogil:
        for i in prange(width, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in prange(height):
                new_array[i, j, 0], new_array[i, j, 1], new_array[i, j, 2], \
                new_array[i, j, 3] =  rgb_array_c[i, j, 0], rgb_array_c[i, j, 1], \
                                   rgb_array_c[i, j, 2], alpha_c[i, j]
    return asarray(new_array)


cpdef make_array(np.ndarray[np.uint8_t, ndim=3] rgb_array_, np.ndarray[np.uint8_t, ndim=2] alpha_):
    """
    CREATE A 3D ARRAY CONTAINING RGBA VALUES
    
    * Return a new array 
    
    :param rgb_array_ : 3d numpy ndarray type (w, h, 3) containing rgb values (unsigned char)
    :param alpha_     : 2d numpy ndarray type (w, h, 2) containing alpha layer
    :return           : 3d numpy ndarray type (w, h, 4) containing rgba values, this array can be converted
                        to a 32 bit pygame surface.
    """
    return dstack((rgb_array_, alpha_))


cpdef make_surface_deprecated(rgba_array: numpy.ndarray):
    """
    CONVERT A 3D NUMPY ARRAY TYPE W x H x 4 INTO A 32bit
    PYGAME SURFACE CONTAINING PER-PIXEL INFORMATION

    :param rgba_array : 3d numpy.ndarray with RGBA values
    :return           : return a pygame.Surface 32 bit with per-pixel information
    """
    warnings.warn("Deprecated version, use make_surface instead", DeprecationWarning)
    return frombuffer((rgba_array.transpose(1, 0, 2)).copy(order='C').astype(numpy.uint8),
                      (rgba_array.shape[:2][0], rgba_array.shape[:2][1]), 'RGBA')


cpdef make_surface(rgba_array: numpy.ndarray):
    """
    CONVERT A 3D NUMPY ARRAY TYPE W x H x 4 INTO A 32bit 
    PYGAME SURFACE CONTAINING PER-PIXEL INFORMATION
    
    * Create a new surface
    
    :param rgba_array : 3d numpy.ndarray with RGBA values  
    :return           : return a pygame.Surface 32 bit with per-pixel information
    """
    cdef tuple c = rgba_array.shape[:2]
    cdef int w = c[0], h = c[1]
    return frombuffer((rgba_array.transpose(1, 0, 2)).tobytes(), (w, h), 'RGBA')


cpdef blend_texture_32c(surface_, final_color_, float percentage):
    """
    BLEND A TEXTURE COLORS TOWARD A GIVEN SOLID COLOR

    * This version is faster than blend_texture_32
    * Create a new surface
    * Compatible with 32-bit surface with per-pixel alpha channel only.
    * Blend a texture with a percentage of given rgb color (using linear lerp method)
      Blend at 100%, all pixels from the original texture will merge toward the given pixel colors. 
      Blend at 0%, texture is unchanged (return)
    * The output image is formatted for a fast blit (convert_alpha()). 

    :param surface_    : 32-bit pygame.Surface with per-pixel transparency
    :param final_color_: Destination color. Can be a pygame color with values RGB, a tuple (RGB) or a 
    list [RGB]. RGB values must be type integer [0..255]
    :param percentage  : float; 0 - 100%, blend percentage
    :return: return a pygame.surface with per-pixels transparency. 
    """

    if PyObject_IsInstance(final_color_, pygame.Color):
        final_color_ = (final_color_.r, final_color_.g, final_color_.b)

    elif PyObject_IsInstance(final_color_, (tuple, list)):
        assert len(final_color_)==3, \
            'Invalid color format, use format (R, G, B) or [R, G, B].'
        pass
    else:
        raise TypeError('Color type argument error.')

    assert PyObject_IsInstance(surface_, Surface), \
        'Argument surface_ must be a Surface got %s ' % type(surface_)

    assert 0.0 <= percentage <= 100.0, \
        "Incorrect value for argument percentage should be [0.0 ... 100.0]  got %s " % percentage

    if percentage == 0:
        return surface_

    cdef unsigned char [:, :, :] source_array
    cdef unsigned char [:, :] alpha_channel
    try:
        source_array = pixels3d(surface_)
    except Exception as e:
        raise ValueError("Cannot reference pixels into a 3d array.\n %s " % e)

    try:
        alpha_channel = pixels_alpha(surface_)
    except Exception as e:
        raise ValueError("Cannot reference pixel alphas into a 2d array..\n %s " % e)

    cdef:
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        unsigned char [:, :, ::1] final_array = empty((h, w, 4), dtype=uint8)
        unsigned char [:] f_color = numpy.array(final_color_[:3], dtype=uint8)  # take only rgb values
        int c1, c2, c3
        float c4 = 1.0 / 100.0
        int i=0, j=0
        unsigned char r, g, b

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r, g, b = source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2]
                c1 = min(<int> (r + ((f_color[0] - r) * c4) * percentage), 255)
                c2 = min(<int> (g + ((f_color[1] - g) * c4) * percentage), 255)
                c3 = min(<int> (b + ((f_color[2] - b) * c4) * percentage), 255)
                if c1 < 0:
                    c1 = 0
                if c2 < 0:
                    c2 = 0
                if c3 < 0:
                    c3 = 0
                final_array[j, i, 0], final_array[j, i, 1], \
                final_array[j, i, 2], final_array[j, i, 3] = c1, c2, c3, alpha_channel[i, j]

    return pygame.image.frombuffer(final_array, (w, h), 'RGBA').convert_alpha()


cpdef void blend_texture_inplace_32c(surface_, final_color_, float percentage):
    """
    BLEND A TEXTURE COLORS TOWARD A GIVEN SOLID COLOR

    * This version is faster than blend_texture_32
    * Blend the surface inplace 
    * Compatible with 32-bit surface with per-pixel alpha channel only.
    * Blend a texture with a percentage of given rgb color (using linear lerp method)
      Blend at 100%, all pixels from the original texture will merge toward the given pixel colors. 
      Blend at 0%, texture is unchanged (return)

    :param surface_    : 32-bit pygame.Surface with per-pixel transparency
    :param final_color_: Destination color. Can be a pygame color with values RGB, a tuple (RGB) or a 
    list [RGB]. RGB values must be type integer [0..255]
    :param percentage  : float; 0 - 100%, blend percentage
    :return: void
    """

    if PyObject_IsInstance(final_color_, pygame.Color):
        final_color_ = (final_color_.r, final_color_.g, final_color_.b)

    elif PyObject_IsInstance(final_color_, (tuple, list)):
        assert len(final_color_)==3, \
            'Invalid color format, use format (R, G, B) or [R, G, B].'
        pass
    else:
        raise TypeError('Color type argument error.')

    assert PyObject_IsInstance(surface_, Surface), \
        'Argument surface_ must be a Surface got %s ' % type(surface_)

    assert 0.0 <= percentage <= 100.0, \
        "Incorrect value for argument percentage should be [0.0 ... 100.0] %s " % percentage

    if percentage == 0:
        return

    cdef unsigned char [:, :, :] source_array
    cdef unsigned char [:, :] alpha_channel

    try:
        source_array = pixels3d(surface_)
    except Exception as e:
        raise ValueError("Cannot reference pixels into a 3d array.\n %s " % e)

    try:
        alpha_channel = pixels_alpha(surface_)
    except Exception as e:
        raise ValueError("Cannot reference pixel alphas into a 2d array..\n %s " % e)

    cdef:
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        unsigned char [:] f_color = numpy.array(final_color_[:3], dtype=uint8)  # take only rgb values
        int c1, c2, c3
        float c4 = 1.0 / 100.0
        int i=0, j=0
        unsigned char r, g, b

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r, g, b = source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2]
                c1 = min(<int> (r + ((f_color[0] - r) * c4) * percentage), 255)
                c2 = min(<int> (g + ((f_color[1] - g) * c4) * percentage), 255)
                c3 = min(<int> (b + ((f_color[2] - b) * c4) * percentage), 255)
                if c1 < 0:
                    c1 = 0
                if c2 < 0:
                    c2 = 0
                if c3 < 0:
                    c3 = 0
                source_array[i, j, 0], source_array[i, j, 1], \
                source_array[i, j, 2], source_array[i, j, 3] = c1, c2, c3, alpha_channel[i, j]


cpdef blend_texture_24c(surface_, final_color_, float percentage):
    """
    BLEND A TEXTURE COLORS TOWARD A GIVEN SOLID COLOR

    * This version is faster than blend_texture_24
    * Create a new surface
    * Compatible with 24-bit surface without transparency
    * Blend a texture with a percentage of given rgb color (using linear lerp method)
      Blend at 100%, all pixels from the original texture will merge toward the given pixel colors. 
      Blend at 0%, texture is unchanged (return)
    * The output image is formatted for a fast blit (convert()). 

    :param surface_    : 24-bit pygame.Surface without transparency
    :param final_color_: Destination color. Can be a pygame color with values RGB, a tuple (RGB) or a 
    list [RGB]. RGB values must be type integer [0..255]
    :param percentage  : float ; 0 - 100%, blend percentage
    :return: return a pygame.surface without transparency and converted for fast blit 
    """

    if PyObject_IsInstance(final_color_, pygame.Color):
        final_color_ = (final_color_.r, final_color_.g, final_color_.b)

    elif PyObject_IsInstance(final_color_, (tuple, list)):
        assert len(final_color_)==3, \
            'Invalid color format, use format (R, G, B) or [R, G, B].'
        pass
    else:
        raise TypeError('Color type argument error.')

    assert PyObject_IsInstance(surface_, Surface), \
        'Argument surface_ must be a Surface got %s ' % type(surface_)

    assert 0.0 <= percentage <= 100.0, \
        "Incorrect value for argument percentage should be [0.0 ... 100.0] %s " % percentage

    if percentage == 0:
        return surface_

    cdef unsigned char[:, :, :] source_array
    try:
        source_array = array3d(surface_)
    except Exception as e:
        raise ValueError("Cannot reference pixels into a 3d array.\n %s " % e)

    cdef:
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        unsigned char [:] f_color = numpy.array(final_color_[:3], dtype=uint8)  # take only rgb values
        int c1, c2, c3
        float c4 = 1.0 / 100.0
        int i=0, j=0
        unsigned char r, g, b

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r, g, b = source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2]
                c1 = min(<int> (r + ((f_color[0] - r) * c4) * percentage), 255)
                c2 = min(<int> (g + ((f_color[1] - g) * c4) * percentage), 255)
                c3 = min(<int> (b + ((f_color[2] - b) * c4) * percentage), 255)
                if c1 < 0:
                    c1 = 0
                if c2 < 0:
                    c2 = 0
                if c3 < 0:
                    c3 = 0
                source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2] = c1, c2, c3

    return pygame.surfarray.make_surface(asarray(source_array)).convert()


cpdef void blend_texture_inplace_24c(surface_, final_color_, float percentage):
    """
    BLEND A TEXTURE COLORS TOWARD A GIVEN SOLID COLOR INPLACE 

    * This version is faster than blend_texture_24
    * Blend the surface inplace 
    * Compatible with 24-bit surface without transparency
    * Blend a texture with a percentage of given rgb color (using linear lerp method)
      Blend at 100%, all pixels from the original texture will merge toward the given pixel colors. 
      Blend at 0%, texture is unchanged (return)
    * The output image is formatted for a fast blit (convert()). 

    :param surface_    : 24-bit pygame.Surface without transparency
    :param final_color_: Destination color. Can be a pygame color with values RGB, a tuple (RGB) or a 
    list [RGB]. RGB values must be type integer [0..255]
    :param percentage  : float ; 0 - 100%, blend percentage
    :return: void
    """

    if PyObject_IsInstance(final_color_, pygame.Color):
        final_color_ = (final_color_.r, final_color_.g, final_color_.b)

    elif PyObject_IsInstance(final_color_, (tuple, list)):
        assert len(final_color_)==3, \
            'Invalid color format, use format (R, G, B) or [R, G, B].'
        pass
    else:
        raise TypeError('Color type argument error.')

    assert PyObject_IsInstance(surface_, Surface), \
        'Argument surface_ must be a Surface got %s ' % type(surface_)

    assert 0.0 <= percentage <= 100.0, \
        "Incorrect value for argument percentage should be [0.0 ... 100.0] %s " % percentage

    if percentage == 0:
        return

    cdef unsigned char [:, :, :] source_array
    try:
        source_array = pixels3d(surface_)
    except Exception as e:
        raise ValueError("Cannot reference pixels into a 3d array.\n %s " % e)

    cdef:
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        unsigned char [:] f_color = numpy.array(final_color_[:3], dtype=uint8)  # take only rgb values
        int c1, c2, c3
        float c4 = 1.0 / 100.0
        int i=0, j=0
        unsigned char r, g, b

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r, g, b = source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2]
                c1 = min(<int> (r + ((f_color[0] - r) * c4) * percentage), 255)
                c2 = min(<int> (g + ((f_color[1] - g) * c4) * percentage), 255)
                c3 = min(<int> (b + ((f_color[2] - b) * c4) * percentage), 255)
                if c1 < 0:
                    c1 = 0
                if c2 < 0:
                    c2 = 0
                if c3 < 0:
                    c3 = 0
                source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2] = c1, c2, c3



cpdef blend_to_textures_24c(source_, destination_, float percentage_):
    """
    BLEND A SOURCE TEXTURE TOWARD A DESTINATION TEXTURE 

    * Video system must be initialised 
    * Textures must be same sizes
    * Compatible with 24-bit surface
    * Create a new surface
    * Image returned is converted for fast blit (convert())

    :param source_     : pygame.Surface (Source)
    :param destination_: pygame.Surface (Destination)
    :param percentage_ : float; Percentage value between [0.0 ... 100.0]
    :return: return    : Return a 24 bit pygame.Surface and blended with a percentage of the destination texture.
    """
    assert PyObject_IsInstance(source_, Surface), \
        'Argument source_ must be a pygame.Surface got %s ' % type(source_)

    assert PyObject_IsInstance(destination_, Surface), \
        'Argument destination_ must be a pygame.Surface got %s ' % type(destination_)

    assert 0.0 <= percentage_ <= 100.0, \
        "\nIncorrect value for argument percentage should be [0.0 ... 100.0] got %s " % percentage_

    if percentage_ == 0.0:
        return source_

    assert source_.get_size() == destination_.get_size(),\
        'Source and Destination surfaces must have same dimensions: ' \
        'Source (w:%s, h:%s), destination (w:%s, h:%s).' % (*source_.get_size(), *destination_.get_size())

    cdef:
            unsigned char [:, :, :] source_array
            unsigned char [:, :, :] destination_array

    try:
        source_array      = pixels3d(source_)
    except Exception as e:
        raise ValueError("\nCannot reference source pixels into a 3d array.\n %s " % e)

    try:
        destination_array = pixels3d(destination_)
    except Exception as e:
        raise ValueError("\nCannot reference destination pixels into a 3d array.\n %s " % e)

    cdef:

        int c1, c2, c3
        int i=0, j=0
        float c4 = 1.0/100.0
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        unsigned char[:, :, :] final_array = empty((h, w, 3), dtype=uint8)
        unsigned char r, g, b

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r, g, b = source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2]
                c1 = min(<int> (r + ((destination_array[i, j, 0] - r) * c4) * percentage_), 255)
                c2 = min(<int> (g + ((destination_array[i, j, 1] - g) * c4) * percentage_), 255)
                c3 = min(<int> (b + ((destination_array[i, j, 2] - b) * c4) * percentage_), 255)
                if c1 < 0:
                    c1 = 0
                if c2 < 0:
                    c2 = 0
                if c3 < 0:
                    c3 = 0
                final_array[j, i, 0], final_array[j, i, 1], final_array[j, i, 2] = c1, c2, c3

    return pygame.image.frombuffer(final_array, (w, h), 'RGB').convert()



cpdef void blend_to_textures_inplace_24c(source_, destination_, float percentage_):
    """
    BLEND A SOURCE TEXTURE TOWARD A DESTINATION TEXTURE (INPLACE)

    * Video system must be initialised 
    * Textures must be same sizes
    * Compatible with 24-bit surface 
    * Change apply inplace
    * Image returned is converted for fast blit (convert())

    :param source_     : pygame.Surface (Source)
    :param destination_: pygame.Surface (Destination)
    :param percentage_ : float; Percentage value between [0.0 ... 100.0]
    :return: return    : void
    """

    assert PyObject_IsInstance(source_, Surface), \
        'Argument source_ must be a pygame.Surface got %s ' % type(source_)

    assert PyObject_IsInstance(destination_, Surface), \
        'Argument destination_ must be a pygame.Surface got %s ' % type(destination_)

    assert 0.0 <= percentage_ <= 100.0, \
        "Incorrect value for argument percentage should be [0.0 ... 100.0] got %s " % percentage_

    if percentage_ == 0:
        return

    assert source_.get_size() == destination_.get_size(),\
        'Source and Destination surfaces must have same dimensions: ' \
        'Source (w:%s, h:%s), destination (w:%s, h:%s).' % (*source_.get_size(), *destination_.get_size())

    cdef:
        unsigned char [:, :, :] source_array
        unsigned char[:, :, :] destination_array

    try:
        source_array = pixels3d(source_)
    except Exception as e:
        raise ValueError("Cannot reference source pixels into a 3d array.\n %s " % e)

    try:
        destination_array = pixels3d(destination_)
    except Exception as e:
        raise ValueError("Cannot reference destination pixels into a 3d array.\n %s " % e)

    cdef:
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        int c1, c2, c3
        int i=0, j=0
        float c4 = 1.0/100.0
        unsigned char r, g, b

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r, g, b = source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2]
                c1 = min(<int> (r + ((destination_array[i, j, 0] - r) * c4) * percentage_), 255)
                c2 = min(<int> (g + ((destination_array[i, j, 1] - g) * c4) * percentage_), 255)
                c3 = min(<int> (b + ((destination_array[i, j, 2] - b) * c4) * percentage_), 255)
                if c1 < 0:
                    c1 = 0
                if c2 < 0:
                    c2 = 0
                if c3 < 0:
                    c3 = 0
                source_array[i, j, 0], source_array[i, j, 1],  source_array[i, j, 2] = c1, c2, c3





cpdef blend_to_textures_32c(source_, destination_, float percentage_):
    """
    BLEND A SOURCE TEXTURE TOWARD A DESTINATION TEXTURE 

    * Video system must be initialised 
    * Textures must be same sizes
    * Compatible with 32-bit surface containing per-pixel alpha channel.
    * Create a new surface
    * Image returned is converted for fast blit (convert_alpha())

    :param source_     : pygame.Surface (Source)
    :param destination_: pygame.Surface (Destination)
    :param percentage_ : float; Percentage value between [0, 100]
    :return: return    : Return a 32 bit pygame.Surface containing alpha channel and blended 
    with a percentage of the destination texture.
    """
    assert PyObject_IsInstance(source_, Surface), \
        'Argument source_ must be a pygame.Surface got %s ' % type(source_)

    assert PyObject_IsInstance(destination_, Surface), \
        'Argument destination_ must be a pygame.Surface got %s ' % type(destination_)

    assert 0.0 <= percentage_ <= 100.0, \
        "Incorrect value for argument percentage should be [0.0 ... 100.0] %s " % percentage_

    if percentage_ == 0:
        return source_

    assert source_.get_size() == destination_.get_size(),\
        'Source and Destination surfaces must have same dimensions: ' \
        'Source (w:%s, h:%s), destination (w:%s, h:%s).' % (*source_.get_size(), *destination_.get_size())

    cdef:
            unsigned char [:, :, :] source_array
            unsigned char [:, :, :] destination_array
            unsigned char [:, :] alpha_channel

    try:
        source_array      = pixels3d(source_)
    except Exception as e:
        raise ValueError("\nCannot reference source pixels into a 3d array.\n %s " % e)

    try:
        destination_array = pixels3d(destination_)
    except Exception as e:
        raise ValueError("\nCannot reference destination pixels into a 3d array.\n %s " % e)

    try:
        alpha_channel     = pixels_alpha(source_)
    except Exception as e:
        raise ValueError("\nCannot reference source pixel alphas into a 2d array..\n %s " % e)

    cdef:

        int c1, c2, c3
        int i=0, j=0
        float c4 = 1.0/100.0
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        unsigned char[:, :, :] final_array = empty((h, w, 4), dtype=uint8)
        unsigned char r, g, b
    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r, g, b = source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2]
                c1 = min(<int> (r + ((destination_array[i, j, 0] - r) * c4) * percentage_), 255)
                c2 = min(<int> (g + ((destination_array[i, j, 1] - g) * c4) * percentage_), 255)
                c3 = min(<int> (b + ((destination_array[i, j, 2] - b) * c4) * percentage_), 255)
                if c1 < 0:
                    c1 = 0
                if c2 < 0:
                    c2 = 0
                if c3 < 0:
                    c3 = 0
                final_array[j, i, 0], final_array[j, i, 1], \
                final_array[j, i, 2], final_array[j, i, 3] = c1, c2, c3, alpha_channel[i, j]

    return pygame.image.frombuffer(final_array, (w, h), 'RGBA').convert_alpha()


cpdef void blend_to_textures_inplace_32c(source_, destination_, float percentage_):
    """
    BLEND A SOURCE TEXTURE TOWARD A DESTINATION TEXTURE (INPLACE)

    * Video system must be initialised 
    * Textures must be same sizes
    * Compatible with 32-bit surface containing per-pixel alpha channel.
    * Change apply inplace
    * Image returned is converted for fast blit (convert_alpha())

    :param source_     : pygame.Surface (Source)
    :param destination_: pygame.Surface (Destination)
    :param percentage_ : float; Percentage value between [0, 100]
    :return: return    : void
    """
    assert PyObject_IsInstance(source_, Surface), \
        'Argument source_ must be a pygame.Surface got %s ' % type(source_)

    assert PyObject_IsInstance(destination_, Surface), \
        'Argument destination_ must be a pygame.Surface got %s ' % type(destination_)

    assert 0.0 <= percentage_ <=100.0, \
        "Incorrect value for argument percentage should be [0.0 ... 100.0] %s " % percentage_

    if percentage_ == 0:
        return

    assert source_.get_size() == destination_.get_size(),\
        'Source and Destination surfaces must have same dimensions: ' \
        'Source (w:%s, h:%s), destination (w:%s, h:%s).' % (*source_.get_size(), *destination_.get_size())

    cdef:
        unsigned char [:, :, :] source_array
        unsigned char[:, :, :] destination_array
        unsigned char[:, :] alpha_channel
    try:
        source_array = pixels3d(source_)
    except Exception as e:
        raise ValueError("Cannot reference source pixels into a 3d array.\n %s " % e)

    try:
        destination_array = pixels3d(destination_)
    except Exception as e:
        raise ValueError("Cannot reference destination pixels into a 3d array.\n %s " % e)

    try:
        alpha_channel = pixels_alpha(source_)
    except Exception as e:
        raise ValueError("Cannot reference source pixel alphas into a 2d array..\n %s " % e)

    cdef:
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        int c1, c2, c3
        int i=0, j=0
        float c4 = 1.0/100.0
        unsigned char r, g, b

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r, g, b = source_array[i, j, 0], source_array[i, j, 1], source_array[i, j, 2]
                c1 = min(<int> (r + ((destination_array[i, j, 0] - r) * c4) * percentage_), 255)
                c2 = min(<int> (g + ((destination_array[i, j, 1] - g) * c4) * percentage_), 255)
                c3 = min(<int> (b + ((destination_array[i, j, 2] - b) * c4) * percentage_), 255)
                if c1 < 0:
                    c1 = 0
                if c2 < 0:
                    c2 = 0
                if c3 < 0:
                    c3 = 0
                source_array[i, j, 0], source_array[i, j, 1], \
                source_array[i, j, 2], source_array[i, j, 3] = c1, c2, c3, alpha_channel[i, j]


cpdef make_transparent32(surface_, int alpha_value):
    """
    MODIFY TRANSPARENCY TO A PYGAME SURFACE 
    
    * Video system must be initialised 
    * Compatible with 32-bit surface with transparency layer 
    * Create a new 32-bit surface with transparency layer converted to fast blit (convert_alpha())
    
    :param surface_   : Surface; pygame.Surface to modify  
    :param alpha_value: integer; integer value representing the alpha value to subtract range [0 ... 255]
    :return : 32-bit Surface with new alpha value (with transparency layer)
    """
    cdef:
        unsigned char [:, :] alpha_array
        unsigned char [:, :, :] rgb_array

    try:
        rgb_array = pixels3d(surface_)
    except (pygame.error, ValueError):
        raise ValueError('Invalid surface.')

    try:
        alpha_array = pixels_alpha(surface_)
    except (pygame.error, ValueError):
        raise ValueError('Surface without per-pixel information.')

    cdef int w, h
    w, h = surface_.get_size()

    cdef:
        unsigned char [:, :, ::1] new_array = numpy.empty((h, w, 4), dtype=numpy.uint8)
        int i=0, j=0, a

    with nogil:

        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                new_array[j, i, 0] = rgb_array[i, j, 0]
                new_array[j, i, 1] = rgb_array[i, j, 1]
                new_array[j, i, 2] = rgb_array[i, j, 2]
                a = alpha_array[i, j] - alpha_value
                if a < 0:
                    a = 0
                new_array[j, i, 3] = a

    return frombuffer(new_array, (w, h), 'RGBA').convert_alpha()

cpdef void make_transparent32_inplace(image_, int alpha_):
    """
    MODIFY TRANSPARENCY TO A PYGAME SURFACE (INPLACE)
    
    * Video system must be initialised 
    * Compatible with 32-bit surface with transparency layer 
    * Change apply inplace

    :param image_: Surface; pygame.Surface to modify  
    :param alpha_: integer; integer value representing the alpha value to subtract range [0 ... 255]
    :return      : void
    """
    cdef unsigned char [:, :] alpha_array
    try:
        alpha_array = pixels_alpha(image_)
    except (pygame.error, ValueError):
        raise ValueError('Surface without per-pixel information.')

    cdef int w, h
    w, h = image_.get_size()

    cdef:
        int i=0, j=0, a

    with nogil:

        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                a = alpha_array[i, j] - alpha_
                if a < 0:
                    a = 0
                alpha_array[i, j] = a


cpdef void blink_surface32_inplace(image_, int alpha_):
    """
    MODIFY TRANSPARENCY TO A PYGAME SURFACE (INPLACE). 
    ALPHA VALUE IS ROTATING FROM 255 -> 0 -> 255 CREATING A BLINKING EFFECT

    * Video system must be initialised 
    * Compatible with 32-bit surface with transparency layer 
    * Change apply inplace

    :param image_: Surface; pygame.Surface to modify  
    :param alpha_: integer; integer value representing the alpha value to subtract range [0 ... 255]
    :return      : void
    """
    cdef unsigned char [:, :] alpha_array
    try:
        alpha_array = pixels_alpha(image_)
    except (pygame.error, ValueError):
        raise ValueError('Surface without per-pixel information.')

    cdef int w, h
    w, h = image_.get_size()

    cdef:
        int i=0, j=0

    with nogil:

        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                alpha_array[i, j] = <unsigned char> (alpha_array[i, j] - alpha_)


# Deprecated
cpdef TransparencyPixelFilter(unsigned char [:, :, :] rgb_array,
                              unsigned char [:, :] alpha_array,
                              int new_alpha,
                              int threshold):

    """
    MODIFY TRANSPARENCY FOR ALPHA PIXEL VALUES < THRESHOLD 

    * Video system must be initialised 
    * Change alpha values if r < threshold and g < threshold and b < threshold 
    * Return a 32-bit surface with per-pixel transparency (build from rgb_array and alpha_array). 
      The newly created image is converted for fast blit (convert_alpha)

    :param rgb_array   : 3d numpy ndarray representing the pixels RGB values   
    :param alpha_array : 2d numpy ndarray representing the layer alpha 
    :param new_alpha   : integer; New alpha value 
    :param threshold   : integer; Threshold to compare to the sum RGB 
    :return            : 32bit Pygame Surface  (containing per-pixel information) and converted for 
    fast blit (convert_alpha)
    """
    warnings.warn("Deprecated version, use TransparencyPixelFilter_c instead", DeprecationWarning)

    assert PyObject_IsInstance(new_alpha, int), 'Expecting int got %s ' % type(new_alpha)
    assert PyObject_IsInstance(threshold, int), 'Expecting int got %s ' % type(threshold)

    if 0 > new_alpha > 255:
        raise ValueError('Invalid value for argument new_alpha, '
                         'should be 0 <= alpha_value <=255 got %s ' % new_alpha)
    if 0 > threshold > 255:
        raise ValueError('Invalid value for argument threshold, '
                         'should be 0 <= threshold <=255 got %s ' % threshold)

    rgba = make_array_cython(rgb_array, alpha_array)
    red, green, blue, alpha_ = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2], rgba[:, :, 3]
    mask1 = (red < threshold) & (green < threshold) & (blue < threshold)
    mask2 = alpha_ > 0
    mask = mask1 & mask2
    rgba[:, :, :][mask] = new_alpha
    return make_surface(rgba.astype(dtype=numpy.uint8)).convert_alpha()


cpdef TransparencyPixelFilter_c(unsigned char [:, :, :] rgb_array, unsigned char [:, :] alpha_array,
                                int new_alpha, int threshold):
    """
    MODIFY TRANSPARENCY FOR ALPHA PIXEL VALUES < THRESHOLD 

    * Video system must be initialised 
    * Change alpha values if r < threshold and g < threshold and  b < threshold
    * Return a 32-bit surface with per-pixel transparency (build from rgb_array and alpha_array). 
      The newly created image is converted for fast blit (convert_alpha)

    :param rgb_array   : 3d numpy ndarray representing the pixels RGB values   
    :param alpha_array : 3d numpy ndarray representing the layer alpha 
    :param new_alpha   : integer; New alpha value 
    :param threshold   : integer; Threshold to compare to the sum RGB 
    :return            : 32bit Pygame Surface  (containing per-pixel information) and converted for 
    fast blit (convert_alpha)
    """

    assert PyObject_IsInstance(new_alpha, int), 'Expecting int got %s ' % type(new_alpha)
    assert PyObject_IsInstance(threshold, int), 'Expecting int got %s ' % type(threshold)

    if 0 > new_alpha > 255:
        raise ValueError('Invalid value for argument new_alpha, '
                         'should be 0 <= alpha_value <=255 got %s ' % new_alpha)
    if 0 > threshold > 255:
        raise ValueError('Invalid value for argument threshold, '
                         'should be 0 <= threshold <=255 got %s ' % threshold)

    cdef:
        int w, h, n, w1, h1

    w, h, n = (<object>rgb_array).shape
    w1, h1 = (<object>alpha_array).shape

    cdef unsigned char [:, :] output_alpha_array = alpha_array

    if w != w1 or h != h1:
        raise ValueError('rgb_array (%s, %s, %s) and alpha_array '
                         '(%s, %s) are not equivalent!' % (w, h, n, w1, h1))

    cdef:
        int i=0, j=0

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                if rgb_array[i, j, 0] < threshold and rgb_array[i, j, 1] < threshold \
                        and rgb_array[i, j, 2] < threshold:
                    output_alpha_array[i, j] = new_alpha

    return make_surface(make_array_cython(rgb_array, output_alpha_array)).convert_alpha()



cpdef TransparencyPixelFilter_inplace_c(surface_, int new_alpha, int threshold):
    """
    MODIFY TRANSPARENCY FOR ALPHA PIXEL VALUES < THRESHOLD 

    * Video system must be initialised 
    * Change alpha values if r < threshold and g < threshold and  b < threshold
    * Return a 32-bit surface with per-pixel transparency (build from rgb_array and alpha_array). 
      The newly created image is converted for fast blit (convert_alpha)

    :param surface_    : pygame surface 32-bit with transparency
    :param new_alpha   : integer; New alpha value 
    :param threshold   : integer; Threshold to compare to the sum RGB 
    :return            : 32bit Pygame Surface  (containing per-pixel information) and converted for 
    fast blit (convert_alpha)
    """

    assert PyObject_IsInstance(new_alpha, int), 'Expecting int got %s ' % type(new_alpha)
    assert PyObject_IsInstance(threshold, int), 'Expecting int got %s ' % type(threshold)

    if 0 > new_alpha > 255:
        raise ValueError('Invalid value for argument new_alpha, '
                         'should be 0 <= alpha_value <=255 got %s ' % new_alpha)
    if 0 > threshold > 255:
        raise ValueError('Invalid value for argument threshold, '
                         'should be 0 <= threshold <=255 got %s ' % threshold)

    cdef:
        int w, h
        cdef unsigned char [:, :, :] rgb_array
        cdef unsigned char [:, :] alpha_array
    try:
        rgb_array = pixels3d(surface_)
        alpha_array = pixels_alpha(surface_)

    except Exception:
        raise ValueError('Invalid surface.')

    w, h = surface_.get_size()

    cdef:
        int i=0, j=0

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                if rgb_array[i, j, 0] < threshold and rgb_array[i, j, 1] < threshold \
                        and rgb_array[i, j, 2] < threshold:
                    alpha_array[i, j] = new_alpha


# deprecated
cpdef black_blanket(rgb_array: numpy.ndarray, alpha_array: numpy.ndarray, new_alpha, threshold):
    """
    THIS METHOD IS EQUIVALENT TO TransparencyPixelFilter

    """
    warnings.warn("Deprecated version, use TransparencyPixelFilter_c instead", DeprecationWarning)

    assert isinstance(rgb_array, numpy.ndarray), \
        'Expecting numpy.array got %s ' % type(rgb_array)
    assert isinstance(alpha_array, numpy.ndarray), \
        ' Expecting numpy.array got %s ' % type(alpha_array)
    assert isinstance(new_alpha, int), 'Expecting int got %s ' % type(new_alpha)
    assert isinstance(threshold, int), 'Expecting int got %s ' % type(threshold)

    if not 0 <= new_alpha <= 255:
        raise ValueError('Invalid value for argument new_alpha, should be 0 <= alpha_value <=255 got %s '
                    % new_alpha)
    if not 0 <= threshold <= 255:
        raise ValueError('Invalid value for argument threshold, should be 0 <= threshold <=255 got %s '
                    % threshold)

    rgba = make_array(rgb_array, alpha_array)
    red, green, blue, alpha_ = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2], rgba[:, :, 3]
    mask1 = (red < threshold) & (green < threshold) & (blue < threshold)
    mask2 = alpha_ > 0
    mask = mask1 & mask2
    rgba[:, :, :][mask] = new_alpha

    return make_surface(rgba.astype(dtype=numpy.uint8)).convert_alpha()



cpdef smooth_reshape(sprite_, factor_=1.0):
    """
    RESHAPE ANIMATION OR IMAGE USING PYTHON SMOOTHSCALE ALGORITHM

    :param sprite_: list, list containing the surfaces to rescale
    :param factor_: float, int or tuple; Represent the scale factor (new size)
    :return       : return  animation or a single sprite (rescale) 
    """

    cdef:
        float f_factor_
        tuple t_factor_

    if PyObject_IsInstance(factor_, (float, int)):
        # FLOAT OR INT
        try:
            f_factor_ = <float>factor_
            if f_factor_ == 1.0:
                return sprite_
        except ValueError:
            raise ValueError('Argument factor_ must be float or int got %s ' % type(factor_))
    # TUPLE
    else:
        try:
            t_factor_ = tuple(factor_)
            if <float>t_factor_[0] == 0.0 and <float>t_factor_[1] == 0.0:
                return sprite_
        except ValueError:
            raise ValueError('Argument factor_ must be a list or tuple got %s ' % type(factor_))

    cdef:
        int i = 0
        int w, h
        int c1, c2
        sprite_copy = sprite_.copy()

    if PyObject_IsInstance(factor_, (float, int)):
        if PyObject_IsInstance(sprite_, list):
            c1 = <int>(sprite_[i].get_width()  * factor_)
            c2 = <int>(sprite_[i].get_height() * factor_)
        else:
            c1 = <int>(sprite_.get_width()  * factor_)
            c2 = <int>(sprite_.get_height() * factor_)

    # ANIMATION
    if PyObject_IsInstance(sprite_copy, list):

        for surface in sprite_copy:
            if PyObject_IsInstance(factor_, (float, int)):
                sprite_copy[i] = smoothscale(surface, (c1, c2))
            elif PyObject_IsInstance(factor_, (tuple, list)):
                sprite_copy[i] = smoothscale(surface, (factor_[0], factor_[1]))
            else:
                raise ValueError('Argument factor_ incorrect '
                             'type must be float, int or tuple got %s ' % type(factor_))
            i += 1

    # SINGLE IMAGE
    else:
        if PyObject_IsInstance(factor_, (float, int)):
            sprite_copy = smoothscale(sprite_copy,(c1, c2))
        elif PyObject_IsInstance(factor_, (tuple, list)):
            sprite_copy = smoothscale(sprite_copy,factor_[0], factor_[1])
        else:
            raise ValueError('Argument factor_ incorrect '
                             'type must be float, int or tuple got %s ' % type(factor_))

    return sprite_copy

cpdef reshape(sprite_, factor_=1.0):
    """
    RESHAPE ANIMATION OR IMAGE USING PYGAME SCALE ALGORITHM

    :param sprite_: list, CREDIT_SPRITE; list containing the surface to rescale
    :param factor_: float, int or tuple; Represent the scale factor (new size)
    :return       : return  animation or a single CREDIT_SPRITE (rescale) 
    """

    cdef:
        float f_factor_
        tuple t_factor_

    if PyObject_IsInstance(factor_, (float, int)):
        # FLOAT OR INT
        try:
            f_factor_ = <float>factor_
            if f_factor_ == 1.0:
                return sprite_
        except ValueError:
            raise ValueError('Argument factor_ must be float or int got %s ' % type(factor_))
    # TUPLE
    else:
        try:
            t_factor_ = tuple(factor_)
            if <float>t_factor_[0] == 0.0 and <float>t_factor_[1] == 0.0:
                return sprite_
        except ValueError:
            raise ValueError('Argument factor_ must be a list or tuple got %s ' % type(factor_))

    cdef:
        int i = 0
        int w, h
        int c1, c2
        sprite_copy = sprite_.copy()

    if PyObject_IsInstance(factor_, (float, int)):
        if PyObject_IsInstance(sprite_, list):
            c1 = <int>(sprite_[i].get_width()  * factor_)
            c2 = <int>(sprite_[i].get_height() * factor_)
        else:
            c1 = <int>(sprite_.get_width()  * factor_)
            c2 = <int>(sprite_.get_height() * factor_)

    # ANIMATION
    if PyObject_IsInstance(sprite_copy, list):

        for surface in sprite_copy:
            if PyObject_IsInstance(factor_, (float, int)):
                sprite_copy[i] = scale(surface, (c1, c2))
            elif PyObject_IsInstance(factor_, (tuple, list)):
                sprite_copy[i] = scale(surface, (factor_[0], factor_[1]))
            else:
                raise ValueError('Argument factor_ incorrect '
                             'type must be float, int or tuple got %s ' % type(factor_))
            i += 1

    # SINGLE IMAGE
    else:
        if PyObject_IsInstance(factor_, (float, int)):
            sprite_copy = scale(sprite_copy,(c1, c2))
        elif PyObject_IsInstance(factor_, (tuple, list)):
            sprite_copy = scale(sprite_copy,factor_[0], factor_[1])
        else:
            raise ValueError('Argument factor_ incorrect '
                             'type must be float, int or tuple got %s ' % type(factor_))

    return sprite_copy


cpdef wave_xy_c(texture, float rad, int size):
    """
    Create a wave effect on a texture

    e.g:
    for angle in range(0, 360):
        surface = wave_xy(CREDIT_SPRITE, 8 * r * math.pi/180, 10)

    :param texture: pygame.Surface, CREDIT_SPRITE compatible format 24, 32-bit without per-pixel information
    :param rad: float,  angle in radian
    :param size: block size to copy (pixels)
    :return: returns a pygame.Surface 24-bit without per-pixel information
    """
    assert isinstance(texture, Surface), \
        'Argument texture must be a Surface got %s ' % type(texture)
    assert isinstance(rad, float), \
        'Argument rad must be a python float got %s ' % type(rad)
    assert isinstance(size, int), \
        'Argument size must be a python int got %s ' % type(size)

    try:
        rgb_array = pixels3d(texture)

    except (pygame.error, ValueError):
        # unsupported colormasks for alpha reference array
        print('Unsupported colormasks for alpha reference array.')
        raise ValueError('\nIncompatible pixel format.')

    cdef int w, h, dim
    try:
        w, h, dim = rgb_array.shape[:3]
    except (ValueError, pygame.error) as e:
        raise ValueError('Array shape not understood.')

    assert w != 0 or h !=0,\
            'Array with incorrect shape (w>0, h>0, 3) got (w:%s, h:%s, %s) ' % (w, h, dim)
    cdef:
        unsigned char [:, :, ::1] wave_array = zeros((h, w, 3), dtype=uint8)
        unsigned char [:, :, :] rgb = rgb_array
        int x, y, x_pos, y_pos, xx, yy
        int i=0, j=0
        float c1 = 1.0 / float(size * size)
        int w_1 = w - 1
        int h_1 = h - 1

    with nogil:
        for x in prange(0, w_1 - size, size, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            x_pos = x + size + <int>(sin(rad + <float>x * c1) * <float>size)
            for y in prange(0, h_1 - size, size, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
                y_pos = y + size + <int>(sin(rad + <float>y * c1) * <float>size)
                for i in range(0, size + 1):
                    for j in range(0, size + 1):
                        xx = x_pos + i
                        yy = y_pos + j

                        if xx > w_1:
                            xx = w_1
                        elif xx < 0:
                            xx = 0
                        if yy > h_1:
                            yy = h_1
                        elif yy < 0:
                            yy = 0
                        wave_array[yy, xx, 0] = rgb[x + i, y + j, 0]
                        wave_array[yy, xx, 1] = rgb[x + i, y + j, 1]
                        wave_array[yy, xx, 2] = rgb[x + i, y + j, 2]

    return pygame.image.frombuffer(wave_array, (w, h), 'RGB').convert()


cpdef wave_xy_32c(texture, float rad, int size):
    """
    Create a wave effect on a texture

    e.g:
    for angle in range(0, 360):
        surface = wave_xy_32c(texture, 8 * r * math.pi/180, 10)

    :param texture: pygame.Surface, texture compatible format 24, 32-bit without per-pixel information
    :param rad: float,  angle in radian
    :param size: block size to copy (pixels)
    :return: returns a pygame.Surface 24-bit without per-pixel information
    """
    assert isinstance(texture, Surface), \
        'Argument texture must be a Surface got %s ' % type(texture)
    assert isinstance(rad, float), \
        'Argument rad must be a python float got %s ' % type(rad)
    assert isinstance(size, int), \
        'Argument size must be a python int got %s ' % type(size)

    try:
        rgb_array = pixels3d(texture)
        alpha     = pixels_alpha(texture)

    except (pygame.error, ValueError):
        # unsupported colormasks for alpha reference array
        print('Unsupported colormasks for alpha reference array.')
        raise ValueError('Incompatible pixel format.')

    cdef int w, h, dim
    try:
        w, h, dim = rgb_array.shape[:3]
    except (ValueError, pygame.error) as e:
        raise ValueError('Array shape not understood.')

    assert w != 0 or h !=0,\
            'Array with incorrect shape (w>0, h>0, 3) got (w:%s, h:%s, %s) ' % (w, h, dim)
    cdef:
        unsigned char [:, :, ::1] wave_array = zeros((h, w, 4), dtype=uint8)
        unsigned char [:, :, :] rgb = rgb_array
        unsigned char [:, :] alpha_ = alpha
        int x, y, x_pos, y_pos, xx, yy
        int i=0, j=0
        float c1 = 1.0 / float(size * size)
        int w_1 = w - 1
        int h_1 = h - 1

    with nogil:
        for x in prange(0, w_1 - size, size, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            x_pos = x + size + <int>(sin(rad + <float>(x) * c1) * <float>(size))
            for y in range(0, h_1 - size, 10):
                y_pos = y + size + <int>(sin(rad + <float>(y) * c1) * <float>(size))
                for i in range(0, size + 1):
                    for j in range(0, size + 1):
                        xx = x_pos + i
                        yy = y_pos + j

                        if xx > w_1:
                            xx = w_1
                        elif xx < 0:
                            xx = 0
                        if yy > h_1:
                            yy = h_1
                        elif yy < 0:
                            yy = 0
                        wave_array[yy, xx, 0] = rgb[x + i, y + j, 0]
                        wave_array[yy, xx, 1] = rgb[x + i, y + j, 1]
                        wave_array[yy, xx, 2] = rgb[x + i, y + j, 2]
                        wave_array[yy, xx, 3] = alpha_[x + i, y + j]
    return pygame.image.frombuffer(wave_array, (w, h), 'RGBA').convert_alpha()


# horizontal_glitch(surface, 1, 0.3, (50+r)% 20) with r in range [0, 360]
# horizontal_glitch(surface, 1, 0.3, (50-r)% 20) with r in range [0, 360]
cpdef horizontal_glitch24(texture_, double rad1_, double frequency_, double amplitude_):
    """
    HORIZONTAL GLITCH EFFECT
    AFFECT THE ENTIRE TEXTURE BY ADDING PIXEL DEFORMATION
    HORIZONTAL_GLITCH_C(TEXTURE_, 1, 0.1, 10)

    :param texture_  :
    :param rad1_     : Angle deformation in degrees (cos(1) * amplitude will represent the deformation magnitude)
    :param frequency_: Angle in degrees to add every iteration for randomizing the effect
    :param amplitude_: Deformation amplitude, 10 is plenty
    :return:
    """

    try:
        source_array = pygame.surfarray.pixels3d(texture_)
    except (pygame.error, ValueError):
        print('Incompatible texture, must be 24-32bit format.')
        raise ValueError('\nMake sure the surface_ contains per-pixel alpha transparency values.')
    cdef int w, h
    w, h = texture_.get_size()

    cdef:
        int i=0, j=0
        double rad = 3.14/180.0
        double angle = 0.0
        double angle1 = 0.0
        unsigned char [:, :, :] rgb_array = source_array
        unsigned char [:, :, ::1] new_array = numpy.empty((w, h, 3), dtype=numpy.uint8)
        int ii=0

    with nogil:
        for j in range(h):
            for i in range(w):
                ii = (i + <int>(cos(angle) * amplitude_))
                if ii > w - 1:
                    ii = w - 1
                if ii < 0:
                    ii = 0

                new_array[i, j, 0],\
                new_array[i, j, 1],\
                new_array[i, j, 2] = rgb_array[ii, j, 0],\
                    rgb_array[ii, j, 1], rgb_array[ii, j, 2]

            angle1 += frequency_ * rad
            angle += rad1_ * rad + rand() % angle1 - rand() % angle1

    return pygame.surfarray.make_surface(numpy.asarray(new_array)).convert()


cpdef horizontal_glitch32(texture_, double rad1_, double frequency_, double amplitude_):
    """
    HORIZONTAL GLITCH EFFECT
    AFFECT THE ENTIRE TEXTURE BY ADDING PIXEL DEFORMATION
    HORIZONTAL_GLITCH_C(TEXTURE_, 1, 0.1, 10)

    :param texture_  :
    :param rad1_     : Angle deformation in degrees (cos(1) * amplitude will represent the deformation magnitude)
    :param frequency_: Angle in degrees to add every iteration for randomizing the effect
    :param amplitude_: Deformation amplitude, 10 is plenty
    :return:
    """

    try:
        source_array = pixels3d(texture_)
        source_alpha = pixels_alpha(texture_)
    except (pygame.error, ValueError):
        print('Incompatible texture, must be 32bit format.')
        raise ValueError('\nMake sure the surface_ contains per-pixel alpha transparency values.')
    cdef int w, h
    w, h = texture_.get_size()

    cdef:
        int i=0, j=0
        double rad = 3.14/180.0
        double angle = 0.0
        double angle1 = 0.0
        unsigned char [:, :, :] rgb_array = source_array
        unsigned char [:, :] alpha_array  = source_alpha
        unsigned char [:, :, :] new_array = empty((h, w, 4), dtype=uint8)
        int ii=0

    with nogil:
        for j in range(h):
            for i in range(w):
                ii = (i + <int>(cos(angle) * amplitude_))
                if ii > w - 1:
                    ii = w - 1
                if ii < 0:
                    ii = 0

                new_array[j, i, 0],\
                new_array[j, i, 1],\
                new_array[j, i, 2],\
                new_array[j, i, 3] = rgb_array[ii, j, 0],\
                    rgb_array[ii, j, 1], rgb_array[ii, j, 2], alpha_array[ii, j]
            angle1 += frequency_ * rad
            angle += rad1_ * rad + rand() % angle1 - rand() % angle1

    return pygame.image.frombuffer(new_array, (h, w), 'RGBA').convert_alpha()


cpdef vertical_glitch24_c(texture_, double rad1_, double frequency_, double amplitude_):
    """
    Vertical glitch effect
    Affect the entire texture by adding pixel deformation
    vertical_glitch24_c(texture_, 1, 0.1, 10)

    :param texture_:
    :param rad1_: Angle deformation in degrees (cos(1) * amplitude will represent the deformation magnitude)
    :param frequency_: Angle in degrees to add every iteration for randomizing the effect
    :param amplitude_: Deformation amplitude, 10 is plenty
    :return:
    """

    try:
        source_array = pygame.surfarray.pixels3d(texture_)
    except (pygame.error, ValueError):
        # unsupported colormasks for alpha reference array
        print('\nIncompatible texture, must be 24-32bit format.')
        raise ValueError('\nMake sure the surface_ contains per-pixel alpha transparency values.')
    cdef int w, h
    w, h = texture_.get_size()

    cdef:
        int i=0, j=0
        double rad = M_PI/180.0
        double angle = 0.0
        double angle1 = 0.0
        unsigned char [:, :, :] rgb_array = source_array
        unsigned char [:, :, ::1] new_array = numpy.empty((h, w, 3), dtype=numpy.uint8)
        int ii=0

    with nogil:
        for i in range(w):
            for j in range(h):
                ii = (i + <int>(cos(angle) * amplitude_))
                if ii > w - 1:
                    ii = w
                if ii < 0:
                    ii = 0

                new_array[j, i, 0],\
                new_array[j, i, 1],\
                new_array[j, i, 2] = rgb_array[ii, j, 0],\
                    rgb_array[ii, j, 1], rgb_array[ii, j, 2]
            angle1 += frequency_ * rad
            angle += rad1_ * rad + rand() % angle1 - rand() % angle1

    return pygame.image.frombuffer(new_array, (w, h), 'RGB')


cpdef vertical_glitch32_c(texture_, double rad1_, double frequency_, double amplitude_):
    """
    Vertical glitch effect
    Affect the entire texture by adding pixel deformation
    vertical_glitch32_c(texture_, 1, 0.1, 10)

    :param texture_:
    :param rad1_: Angle deformation in degrees (cos(1) * amplitude will represent the deformation magnitude)
    :param frequency_: Angle in degrees to add every iteration for randomizing the effect
    :param amplitude_: Deformation amplitude, 10 is plenty
    :return:
    """

    try:
        source_array = pygame.surfarray.pixels3d(texture_)
    except (pygame.error, ValueError):
        raise ValueError('\nInvalid surface. This version is compatible with 32-bit (with per-pixel transparency)'
                         ' format image only')
    try:
        alpha_array_ = pygame.surfarray.array_alpha(texture_)
    except:
        raise ValueError('\nInvalid surface. This version is compatible with 32-bit (with per-pixel transparency)'
                         ' format image only')

    cdef int w, h
    w, h = texture_.get_size()

    cdef:
        int i=0, j=0
        double rad = M_PI/180.0
        double angle = 0.0
        double angle1 = 0.0
        unsigned char [:, :, :] rgb_array = source_array
        unsigned char [:, :] alpha_array = alpha_array_
        unsigned char [:, :, ::1] new_array = numpy.empty((h, w, 4), dtype=numpy.uint8)
        int ii=0

    with nogil:
        for i in range(w):
            for j in range(h):
                ii = (i + <int>(cos(angle) * amplitude_))
                if ii > w - 1:
                    ii = w
                if ii < 0:
                    ii = 0

                new_array[j, i, 0],\
                new_array[j, i, 1],\
                new_array[j, i, 2] = rgb_array[ii, j, 0],\
                    rgb_array[ii, j, 1], rgb_array[ii, j, 2]
                new_array[j, i, 3] = alpha_array[ii, j]
            angle1 += frequency_ * rad
            angle += rad1_ * rad + rand() % angle1 - rand() % angle1

    return pygame.image.frombuffer(new_array, (h, w), 'RGBA')


cpdef create_horizontal_gradient_1d(int value, tuple start_color=(255, 0, 0), tuple end_color=(0, 255, 0)):
    cdef:
        float [:] diff_ =  numpy.array(end_color, dtype=float32) - \
                            numpy.array(start_color, dtype=float32)
        float [::1] row = numpy.arange(value, dtype=float32) / (value - 1.0)
        unsigned char [:, ::1] rgb_gradient = empty((value, 3), dtype=uint8)
        float [3] start = numpy.array(start_color, dtype=float32)
        int i=0, j=0
    with nogil:
        for i in prange(value, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
               rgb_gradient[i, 0] = <unsigned char>(start[0] + row[i] * diff_[0])
               rgb_gradient[i, 1] = <unsigned char>(start[1] + row[i] * diff_[1])
               rgb_gradient[i, 2] = <unsigned char>(start[2] + row[i] * diff_[2])

    return asarray(rgb_gradient)


cpdef create_horizontal_gradient_3d(int width, int height, tuple start_color=(255, 0, 0), tuple end_color=(0, 255, 0)):
    cdef:
        float [:] diff_ =  numpy.array(end_color, dtype=float32) - \
                            numpy.array(start_color, dtype=float32)
        float [::1] row = numpy.arange(width, dtype=float32) / (width - 1.0)
        unsigned char [:, :, ::1] rgb_gradient = empty((width, height, 3), dtype=uint8)
        float [3] start = numpy.array(start_color, dtype=float32)
        int i=0, j=0
    with nogil:
        for i in prange(width, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(height):
               rgb_gradient[i, j, 0] = <unsigned char>(start[0] + row[i] * diff_[0])
               rgb_gradient[i, j, 1] = <unsigned char>(start[1] + row[i] * diff_[1])
               rgb_gradient[i, j, 2] = <unsigned char>(start[2] + row[i] * diff_[2])

    return asarray(rgb_gradient)



cpdef create_horizontal_gradient_3d_alpha(
        int width, int height, tuple start_color=(255, 0, 0, 0), tuple end_color=(0, 255, 0, 0)):
    cdef:
        float [:] diff_ =  numpy.array(end_color, dtype=float32) - \
                            numpy.array(start_color, dtype=float32)
        float [::1] row = numpy.arange(width, dtype=float32) / (width - 1.0)
        unsigned char [:, :, ::1] rgba_gradient = empty((width, height, 4), dtype=uint8)
        float [4] start = numpy.array(start_color, dtype=float32)
        int i=0, j=0

    with nogil:
        for i in prange(width, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(height):
               rgba_gradient[i, j, 0] = <unsigned char>(start[0] + row[i] * diff_[0])
               rgba_gradient[i, j, 1] = <unsigned char>(start[1] + row[i] * diff_[1])
               rgba_gradient[i, j, 2] = <unsigned char>(start[2] + row[i] * diff_[2])
               rgba_gradient[i, j, 3] = <unsigned char> (start[3] + row[i] * diff_[3])

    return asarray(rgba_gradient)



cdef premultiply_3darray(unsigned char [:, :, :] array_, float [:, :] alpha_, int w, int h, bint transpose = False):
    cdef int i, j

    cdef float [:, :, :] premult_array = numpy.empty((w, h, 3), dtype=float32)
    cdef float [:, :, :] premult_array_transpose = numpy.empty((h, w, 3), dtype=float32)
    cdef float c = 0
    if not transpose:
        with nogil:
            for i in prange(w):
                for j in range(h):
                    # alpha must have same dimension width and height
                    c = alpha_[i, j] / 255.0
                    if c>1.0: c=1.0
                    premult_array[i, j, 0], premult_array[i, j, 1], premult_array[i, j, 2] = \
                        array_[i, j, 0] * c,  array_[i, j, 1] * c, array_[i, j, 2] * c
        return premult_array
    else:
        with nogil:
            for i in prange(w):
                for j in range(h):
                    # works only if alpha_ is transposed
                    c = alpha_[j, i] / 255.0
                    if c>1.0: c = 1.0
                    premult_array_transpose[i, j, 0], premult_array_transpose[i, j, 1], premult_array_transpose[i, j, 2] = \
                        array_[j, i, 0] * c,  array_[j, i, 1] * c, array_[j, i, 2] * c

        return premult_array_transpose

cdef premultiply_2darray(unsigned char [:, :] array_, float [:, :] alpha_, int w, int h, bint transpose=False):
    cdef int i, j
    cdef float [:, :] premult_array= numpy.empty((w, h), dtype=float32)
    cdef float [:, :] premult_array_transpose = numpy.empty((h, w), dtype=float32)
    cdef float c = 0.0
    if not transpose:
        with nogil:
            for i in prange(w):
                for j in range(h):
                    c = array_[i, j] / 255.0 * alpha_[i, j]
                    if c>1.0: c=1.0
                    premult_array[i, j] = c
        return premult_array
    else:
        with nogil:
            for i in prange(w):
                for j in range(h):
                    # alpha_ must be transposed
                    c = array_[j, i] / 255.0 * alpha_[j, i]
                    if c > 1.0: c = 1.0
                    premult_array_transpose[i, j] = c
        return premult_array_transpose




cdef normalized_2darray(unsigned char [:, :] array_, int w, int h, bint transpose=False):
    cdef int i, j
    cdef float [:, :] norm_array= numpy.empty((w, h), dtype=float32)
    cdef float [:, :] norm_array_transpose = numpy.empty((h, w), dtype=float32)

    if not transpose:
        with nogil:
            for i in prange(w):
                for j in range(h):
                    norm_array[i, j] = array_[i, j] / 255.0
        return norm_array
    else:
        with nogil:
            for i in prange(w):
                for j in range(h):
                    # alpha_ must be transposed
                    norm_array_transpose[i, j] = array_[j, i] / 255.0
        return norm_array_transpose



cdef un_normalized_2darray(float [:, :] array_, int w, int h, bint transpose=False):
    cdef int i, j
    cdef unsigned char [:, :] norm_array= numpy.empty((w, h), dtype=uint8)
    cdef unsigned char [:, :] norm_array_transpose = numpy.empty((h, w), dtype=uint8)

    if not transpose:
        with nogil:
            for i in prange(w):
                for j in range(h):
                    norm_array[i, j] = <unsigned char>(array_[i, j] * 255.0)
        return norm_array
    else:
        with nogil:
            for i in prange(w):
                for j in range(h):
                    # alpha_ must be transposed
                    norm_array_transpose[i, j] = <unsigned char>(array_[j, i] * 255.0)
        return norm_array_transpose


cdef un_normalized_4darray(float [:, :, :] array_, int w, int h, bint transpose=False):
    cdef int i, j
    cdef unsigned char [:, :, :] norm_array= numpy.empty((w, h, 4), dtype=uint8)
    cdef unsigned char [:, :, :] norm_array_transpose = numpy.empty((h, w, 4), dtype=uint8)

    if not transpose:
        with nogil:
            for i in prange(w):
                for j in range(h):
                    norm_array[i, j, 0] = <unsigned char>(array_[ i, j, 1] * 255.0)
                    norm_array[i, j, 1] = <unsigned char> (array_[i, j, 2] * 255.0)
                    norm_array[i, j, 2] = <unsigned char> (array_[i, j, 3] * 255.0)
                    norm_array[i, j, 3] = <unsigned char> (array_[i, j, 4] * 255.0)
        return norm_array
    else:
        with nogil:
            for i in prange(w):
                for j in range(h):
                    # alpha_ must be transposed
                    norm_array_transpose[i, j, 1] = <unsigned char>(array_[ j, i, 1] * 255.0)
                    norm_array_transpose[i, j, 2] = <unsigned char> (array_[j, i, 2] * 255.0)
                    norm_array_transpose[i, j, 3] = <unsigned char> (array_[j, i, 3] * 255.0)
                    norm_array_transpose[i, j, 4] = <unsigned char> (array_[j, i, 4] * 255.0)
        return norm_array_transpose


cpdef transition(surface1_, surface2_, set_alpha1_, set_alpha2_, mask_=None):

    """
    ALPHA COMPOSITING / BLEND BETWEEN TWO SURFACES. 
    WHEN ALPHA1 IS 1.0 THE OUTPUT IMAGE IS SURFACE2. WHEN ALPHA1 IS 0.0, BOTH IMAGES ARE MERGED
    SURFACE1, SURFACE2 and MASK MUST HAVE THE SAME DIMENSIONS (WIDTH AND HEIGHT).
    THE MASK ALPHA MUST BE NORMALIZED.
    set_alpha1_ & set_alpha2_ MUST BE IN RANGE [0.0 ... 1.0]
    
    Premultiplied values 
    Calculations for RGB values -> outRGB = SrcRGB + DstRGB(1 - SrcA)
    Calculation  for alpha channel -> outA = SrcA + DstA(1 - SrcA)
    
    e.g : 
    image = transition(surface1, surface2, set_alpha1_=0.1, set_alpha2_=0.5,
                       mask_=(pygame.surfarray.array_alpha(surface1)/255.0).astype(float32))
    
    
    :param surface1_  : pygame.Surface; Surface 32 bit with per pixel alpha or convert_alpha (compatible 32bit)
    :param surface2_  : pygame.Surface; Surface 32 bit with per pixel alpha or convert_alpha (compatible 32bit)
    :param set_alpha1_: float; or numpy array; If float, the algo will convert this value into an array of float
     (same value for all pixels)
    :param set_alpha2_: float; or numpy array; If float, the algo will convert this value into an array of float
     (same value for all pixels)
    :param mask_: None or numpy array; mask alpha (normalized values) 
    :return: Return a 24 bit image with both surface blended together (depends on set_alpha1 value)
    """

    # sizes
    cdef:
        int w, h, w2, h2, i, j
        float [:, :] alpha1
        float [:, :] alpha2
        unsigned char [:, :, :] rgb1
        unsigned char [:, :, :] rgb2


    assert 0.0 <= set_alpha1_ <= 1.0, "Argument set_alpha1_ must be in range [0.0 ... 1.0]"
    assert 0.0 <= set_alpha2_ <= 1.0, "Argument set_alpha2_ must be in range [0.0 ... 1.0]"
    w, h = surface1_.get_size()
    w2, h2 = surface2_.get_size()
    if (w, h) != (w2, h2):
        raise ValueError('Transition effect: both surfaces must have the same dimensions')

    cdef unsigned char [:, :, :] output = numpy.zeros((w, h, 4), dtype=uint8)
    cdef float [:, :] mask_alpha = empty((w, h), dtype=float32)
    cdef bint masking = False
    if mask_ is not None:
        mask_alpha = mask_
        masking = True


    if PyObject_IsInstance(set_alpha1_, float):
        alpha1 = numpy.full((w, h), <float>set_alpha1_, dtype=float32)
    else:
        alpha1 = set_alpha1_

    if PyObject_IsInstance(set_alpha2_, float):
        alpha2 = numpy.full((w, h), <float>set_alpha2_, dtype=float32)
    else:
        alpha2 = set_alpha2_

    try:
        rgb1 = surface1_.get_view('3')
    except ValueError as error:
        ValueError('Transition effect is compatible for 24 - 32-bit surfaces only')
    premultiply_3darray(rgb1, alpha1, w, h)  # normalized rgb1 and * alpha1

    try:
        rgb2 = surface2_.get_view('3')
    except ValueError as error:
        raise ValueError("Transition effect is compatible for 24 - 32-bit surfaces only")
    premultiply_3darray(rgb2, alpha2, w2, h2) # normalized rgb1 and * alpha1


    cdef float c1, c2, c3, c0

    with nogil:
        for i in prange(w):
            for j in prange(h):
                # Calculations for RGB values -> outRGB = SrcRGB + DstRGB(1 - SrcA)
                if masking:
                    if not mask_alpha[i, j] == 0:
                        c0 = 1.0 - alpha1[i, j]
                        c1 = rgb1[i, j, 0] + rgb2[i, j, 0] * c0
                        c2 = rgb1[i, j, 1] + rgb2[i, j, 1] * c0
                        c3 = rgb1[i, j, 2] + rgb2[i, j, 2] * c0
                        output[i, j, 0] = <unsigned char>c1 if c1 <255.0 else 255
                        output[i, j, 1] = <unsigned char>c2 if c2 <255.0 else 255
                        output[i, j, 2] = <unsigned char>c3 if c3 <255.0 else 255
                    ...
                else:
                    c0 = 1.0 - <float>alpha1[i, j]
                    c1 = <float>rgb1[i, j, 0] + <float>(rgb2[i, j, 0]) * c0
                    c2 = <float>rgb1[i, j, 1] + <float>(rgb2[i, j, 1]) * c0
                    c3 = <float>rgb1[i, j, 2] + <float>(rgb2[i, j, 2]) * c0
                    output[i, j, 0] = <unsigned char> c1 if c1 < 255.0 else 255
                    output[i, j, 1] = <unsigned char> c2 if c2 < 255.0 else 255
                    output[i, j, 2] = <unsigned char> c3 if c3 < 255.0 else 255

                # Calculation for alpha channel -> outA = SrcA + DstA(1 - SrcA)
                output[i, j, 3] = <unsigned char>(
                        (<float>alpha1[i, j] + <float>alpha2[i, j] * (1.0 - <float>alpha1[i, j]))*255.0)

    return pygame.image.frombuffer(asarray(output), (h, w), 'RGBA').convert_alpha()
    # return pygame.surfarray.make_surface(asarray(output[:,:,:3]))#.convert(32, RLEACCEL)



# SHADOW EFFECT
cpdef void shadow_inplace(surface_):
    """
    CREATE A SHADOW IMAGE TO REPRESENTING THE PLAYER AIRCRAFT
    
    :param surface_: pygame Surface;  
    :return: void (change apply inplace)
    """

    cdef int width, height
    width, height = surface_.get_size()

    cdef:
        unsigned char grey
        unsigned char [:, :, :] rgb_array = pixels3d(surface_)
        int i=0, j=0

    with nogil:
        for i in prange(width, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(height):
                grey = <unsigned char>((rgb_array[i, j, 0] + rgb_array[i, j, 1] + rgb_array[i, j, 2]) * 0.01)
                rgb_array[i, j, 0],  rgb_array[i, j, 1], rgb_array[i, j, 2] = grey, grey, grey


cpdef mask_shadow(surface_, mask_):
    """
    MASK A PORTION OF A SHADOW IMAGE USING A PYGAME MASK 
    
    This method is very useful when the aircraft shadow should not be fully drawn on the background, 
    e.g transition between the space background and a platform background (between space and the ground) 

     * White pixels from the mask represent full opacity alpha = 255 and black 
       pixel represent full transparency. Surface_ is a 24 bit surface and does not contains 
       an alpha channels. White pixel from the mask will allow to draw pixels on the output surface 24 bit 
       while black pixel will hide pixels at the same location. The mask will act like the set_colorkey method
     * surface_ and mask_ must have the same dimensions width & height 
    
    :param surface_: pygame Surface;  Shadow image 24 bit image without per pixel transparency 
    :param mask_   : pygame.Mask; Mask to use, the mask must be already converted to a
     Surface (black & white image)
    :return: void (change apply inplace)
    """

    cdef int width, height, w_mask, h_mask
    width, height = surface_.get_size()


    if PyObject_IsInstance(mask_, Surface):
        mask_arr = pixels3d(mask_)

    elif PyObject_IsInstance(mask_, ndarray):
        mask_arr = mask_

    else:
        raise ValueError("Argument mask_ is not a valid type got %s " % type(mask))

    try:
        w_mask, h_mask = mask_arr.shape[0], mask_arr.shape[1]
    except:
        raise ValueError("mask has incorrect dimension mask is w x h x 3")

    if w_mask != width or h_mask !=height:
        raise ValueError("Surface and mask have different width and "
                         "height surface(%s, %s) mask(%s, %s) " % (width, height, w_mask, h_mask))

    cdef:
        unsigned char grey
        unsigned char [:, :, :] rgb_array = pixels3d(surface_)
        unsigned char [:, :, :] mask_array = mask_arr
        int i=0, j=0

    with nogil:
        for i in prange(width, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(height):
                if mask_array[i, j, 0] == 0 and mask_array[i, j, 1] == 0 and mask_array[i, j, 2] == 0:
                    rgb_array[i, j, 0], rgb_array[i, j, 1],  rgb_array[i, j, 2] = 0, 0, 0
    return pygame.surfarray.make_surface(asarray(rgb_array))



# TODO USE THE CYNTHONISE VERSION
# Horizontal glitch effect
cpdef hge(texture_, rad1_, frequency_, amplitude_):
    w, h = texture_.get_size()
    w2, h2 = w >> 1, h >> 1
    vector = Vector2(x=0, y=-1)
    position = Vector2(x=w >> 1, y=h - 1)
    rad = M_PI / 180.0
    angle, angle1 = 0, 0
    glitch = Surface((w, h), SRCALPHA)
    glitch.lock()
    while position.y > 0:
        for x in range(-w2 + amplitude_, w2 - amplitude_):
            glitch.set_at((int(position.x + x), int(position.y)),
                          texture_.get_at((int(position.x + x + cos(angle) * amplitude_),
                                           int(position.y))))
        position += vector
        angle1 += frequency_ * rad
        angle += rad1_ * rad + randRangeFloat(-angle1, angle1)
    glitch.unlock()
    return glitch


cpdef swap_channels24_c(surface_, model):
    """
    :param surface_: pygame.Surface
    :param model: python string; String representing the channel order e.g
    RGB, RBG, GRB, GBR, BRG, BGR etc. letters can also be replaced by the digit 0
    to null the entire channel. e.g : 'R0B' -> no green channel  

    """
    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)

    if len(model) != 3:
        print("\nArgument model is invalid.")
        raise ValueError("Choose between RGB, RBG, GRB, GBR, BRG, BGR")

    rr, gg, bb = list(model)
    order = {'R' : 0, 'G' : 1, 'B' : 2, '0': -1}

    cdef int width, height
    width, height = surface_.get_size()

    try:
        rgb_ = pixels3d(surface_)
    except (pygame.error, ValueError):
        try:
            rgb_ = array3d(surface_)
        except(pygame.error, ValueError):
            raise ValueError('\nIncompatible pixel format.')

    cdef:
        unsigned char [:, :, :] rgb_array = rgb_
        unsigned char [:, :, ::1] new_array = empty((height, width, 3), dtype=uint8)
        int i=0, j=0
        short int ri, gi, bi
    ri = order[rr]
    gi = order[gg]
    bi = order[bb]

    with nogil:
        for i in prange(width):
            for j in range(height):
                if ri == -1:
                    new_array[j, i, 0] = 0
                else:
                    new_array[j, i, 0] = rgb_array[i, j, ri]

                if gi == -1:
                    new_array[j, i, 1] = 0
                else:
                    new_array[j, i, 1] = rgb_array[i, j, gi]

                if bi == -1:
                    new_array[j, i, 2] = 0
                else:
                    new_array[j, i, 2] = rgb_array[i, j, bi]

    return pygame.image.frombuffer(new_array, (width, height), 'RGB')



cpdef swap_channels32_c(surface_, model):
    """
    :param surface_: pygame.Surface
    :param model: python string; String representing the channel order e.g
    RGB, RBG, GRB, GBR, BRG, BGR etc. letters can also be replaced by the digit 0
    to null the entire channel. e.g : 'R0B' -> no green channel  

    """
    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)

    if len(model) != 3:
        print("\nArgument model is invalid.")
        raise ValueError("Choose between RGB, RBG, GRB, GBR, BRG, BGR")

    rr, gg, bb = list(model)
    order = {'R' : 0, 'G' : 1, 'B' : 2, '0': -1}

    cdef int width, height
    width, height = surface_.get_size()

    try:
        rgb_ = pixels3d(surface_)
    except (pygame.error, ValueError):
        try:
            rgb_ = array3d(surface_)
        except(pygame.error, ValueError):
            raise ValueError('\nIncompatible pixel format.')

    try:
        alpha_array_ = array_alpha(surface_)
    except:
        raise ValueError('\nIncompatible pixel format.')

    cdef:
        unsigned char [:, :, :] rgb_array = rgb_
        unsigned char [:, :] alpha_array = alpha_array_
        unsigned char [:, :, ::1] new_array = empty((height, width, 4), dtype=uint8)
        int i=0, j=0
        short int ri, gi, bi
    ri = order[rr]
    gi = order[gg]
    bi = order[bb]

    with nogil:
        for i in prange(width):
            for j in range(height):
                if ri == -1:
                    new_array[j, i, 0] = 0
                else:
                    new_array[j, i, 0] = rgb_array[i, j, ri]

                if gi == -1:
                    new_array[j, i, 1] = 0
                else:
                    new_array[j, i, 1] = rgb_array[i, j, gi]

                if bi == -1:
                    new_array[j, i, 2] = 0
                else:
                    new_array[j, i, 2] = rgb_array[i, j, bi]
                new_array[j, i, 3] = alpha_array[i, j]
    return pygame.image.frombuffer(new_array, (width, height), 'RGBA')


cpdef invert_surface_24bit_inplace(image):
    """
    Inverse RGB color values of an image

    Return an image with inverted colors (such as all pixels -> 255 - pixel color ). 
    Compatible with 24 bit image only.  
    :param image: image (Surface) to invert  
    :return: return a pygame Surface
    """
    cdef:
        unsigned char [:, :, :] array_
    try:
        array_ = pixels3d(image)
    except (pygame.error, ValueError):
        raise ValueError('Incompatible pixel format.')

    cdef int w, h, dim

    try:
        w, h, dim = array_.shape[:3]
    except (ValueError, pygame.error) as e:
        raise ValueError('\nArray shape not understood.')

    assert w != 0 or h !=0,\
            'Array with incorrect shape (w>0, h>0, 3) got (w:%s, h:%s, %s) ' % \
                (w, h, dim)
    cdef:
        int i=0, j=0

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                array_[i, j, 0] = 255 -  array_[i, j, 0]
                array_[i, j, 1] = 255 -  array_[i, j, 1]
                array_[i, j, 2] = 255 -  array_[i, j, 2]


cpdef invert_surface_24bit(image):
    """
    Inverse RGB color values of an image

    Return an image with inverted colors (such as all pixels -> 255 - pixel color ). 
    Compatible with 24 bit image only.  
    :param image: image (Surface) to invert  
    :return: return a pygame Surface
    """
    try:
        array_ = array3d(image)
    except (pygame.error, ValueError):
        raise ValueError('Incompatible pixel format.')

    cdef int w, h, dim
    try:
        w, h, dim = array_.shape[:3]
    except (ValueError, pygame.error) as e:
        raise ValueError('\nArray shape not understood.')

    assert w != 0 or h !=0,\
            'Array with incorrect shape (w>0, h>0, 3) got (w:%s, h:%s, %s) ' % \
                (w, h, dim)
    cdef:
        unsigned char [:, :, :] rgb_array = array_
        unsigned char [:, :, ::1] inverted_array  = empty((h, w, 3), dtype=uint8)
        int i=0, j=0
    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                inverted_array[j, i, 0] = 255 -  rgb_array[i, j, 0]
                inverted_array[j, i, 1] = 255 -  rgb_array[i, j, 1]
                inverted_array[j, i, 2] = 255 -  rgb_array[i, j, 2]
    return pygame.image.frombuffer(inverted_array, (w, h), 'RGB').convert()



cpdef invert_surface_24bit_exclude(image, unsigned char red=0, unsigned char green=0, unsigned char blue=0):
    """
    Inverse RGB color values of an image
    
    * Exclude a specific color from the transformation, default black color

    Return an image with inverted colors (such as all pixels -> 255 - pixel color ). 
    Compatible with 24 bit image only.  
    :param blue: 
    :param green: 
    :param red: 
    :param image: image (Surface) to invert  
    :return: return a pygame Surface
    """
    try:
        array_ = array3d(image)
    except (pygame.error, ValueError):
        raise ValueError('Incompatible pixel format.')

    cdef int w, h, dim
    try:
        w, h, dim = array_.shape[:3]
    except (ValueError, pygame.error) as e:
        raise ValueError('\nArray shape not understood.')

    assert w != 0 or h !=0,\
            'Array with incorrect shape (w>0, h>0, 3) got (w:%s, h:%s, %s) ' % \
                (w, h, dim)
    cdef:
        unsigned char [:, :, :] rgb_array = array_
        unsigned char [:, :, ::1] inverted_array  = empty((h, w, 3), dtype=uint8)
        int i=0, j=0
    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                if rgb_array[i, j, 0] != red and rgb_array[i, j, 1] != green and rgb_array[i, j, 2] != blue:
                    inverted_array[j, i, 0] = 255 -  rgb_array[i, j, 0]
                    inverted_array[j, i, 1] = 255 -  rgb_array[i, j, 1]
                    inverted_array[j, i, 2] = 255 -  rgb_array[i, j, 2]
                else:
                    inverted_array[j, i, 0] = 0
                    inverted_array[j, i, 1] = 0
                    inverted_array[j, i, 2] = 0
    return pygame.image.frombuffer(inverted_array, (w, h), 'RGB')


cpdef invert_surface_32bit_inplace(image):
    """

    Return an image with inverted colors (such as all pixels -> 255 - pixel color ). 
    Compatible with 24 bit image only.  
    :param image: image (Surface) to invert  
    :return: return a pygame Surface with per-pixel transparency (alpha set to 255)
    """
    cdef:
        unsigned char [:] rgb_buffer_
    try:
        rgb_buffer_ = image.get_view('2')

    except (pygame.error, ValueError):
        raise ValueError('Incompatible pixel format.')

    cdef int w, h

    try:
        w, h = image.get_size()
    except (ValueError, pygame.error) as e:
        raise ValueError('\nArray shape not understood.')

    assert w != 0 or h != 0, 'Image with incorrect dimensions (w>0, h>0) got (w:%s, h:%s) ' % (w, h)

    cdef:
        int b_length = rgb_buffer_.length
        int i=0

    with nogil:
        for i in prange(0, b_length, 4, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            rgb_buffer_[i    ] = 255 - rgb_buffer_[i    ]
            rgb_buffer_[i + 1] = 255 - rgb_buffer_[i + 1]
            rgb_buffer_[i + 2] = 255 - rgb_buffer_[i + 2]
            rgb_buffer_[i + 3] = 255




cpdef invert_surface_32bit(image):
    """

    Return an image with inverted colors (such as all pixels -> 255 - pixel color ). 
    Compatible with 24 bit image only.  
    :param image: image (Surface) to invert  
    :return: return a pygame Surface with per-pixel transparency 
    """
    try:
        rgba_buffer_ = image.get_view('2')

    except (pygame.error, ValueError):
        raise ValueError('Incompatible pixel format.')

    cdef int w, h
    try:
        w, h = image.get_size()

    except (ValueError, pygame.error) as e:
        raise ValueError('\nArray shape not understood.')

    assert w != 0 or h !=0,\
            'Image with incorrect dimensions (w>0, h>0) got (w:%s, h:%s) ' % (w, h)
    cdef:
        unsigned char [:] rgba_buffer = numpy.frombuffer(rgba_buffer_, dtype=numpy.uint8)

        int b_length = rgba_buffer_.length
        unsigned char [:] rgba_buffer_inv = numpy.empty(b_length, dtype=numpy.uint8)
        int i=0, j = 0
    with nogil:
        for i in prange(0, b_length, 4, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
                rgba_buffer_inv[i + 0] = 255 -  rgba_buffer[i + 0]
                rgba_buffer_inv[i + 1] = 255 -  rgba_buffer[i + 1]
                rgba_buffer_inv[i + 2] = 255 -  rgba_buffer[i + 2]
                rgba_buffer_inv[i + 3] = rgba_buffer[i + 3]
    return pygame.image.frombuffer(rgba_buffer, (w, h), 'RGBA')



cpdef invert_surface_32bit_exclude(image, unsigned char red=0, unsigned char green=0, unsigned char blue=0):
    """
    Inverse RGB color values of an image

    * Exclude a specific color from the transformation, default black color

    Return an image with inverted colors (such as all pixels -> 255 - pixel color ). 
    Compatible with 32 bit image only.  
    :param blue: 
    :param green: 
    :param red: 
    :param image: image (Surface) to invert  
    :return: return a pygame Surface
    """
    try:
        array_ = array3d(image)
        alpha_ = pixels_alpha(image)
    except (pygame.error, ValueError):
        raise ValueError('Incompatible pixel format.')

    cdef int w, h, dim
    try:
        w, h, dim = array_.shape[:3]
    except (ValueError, pygame.error) as e:
        raise ValueError('\nArray shape not understood.')

    assert w != 0 or h !=0,\
            'Array with incorrect shape (w>0, h>0, 3) got (w:%s, h:%s, %s) ' % \
                (w, h, dim)
    cdef:
        unsigned char [:, :, :] rgb_array = array_
        unsigned char [:, :] alpha = alpha_
        unsigned char [:, :, ::1] inverted_array  = empty((h, w, 4), dtype=uint8)
        int i=0, j=0
    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                if rgb_array[i, j, 0] != red and rgb_array[i, j, 1] != green and rgb_array[i, j, 2] != blue:
                    inverted_array[j, i, 0] = 255 -  rgb_array[i, j, 0]
                    inverted_array[j, i, 1] = 255 -  rgb_array[i, j, 1]
                    inverted_array[j, i, 2] = 255 -  rgb_array[i, j, 2]
                    inverted_array[j, i, 3] = alpha[i, j]
                else:
                    inverted_array[j, i, 0] = 0
                    inverted_array[j, i, 1] = 0
                    inverted_array[j, i, 2] = 0
                    inverted_array[j, i, 3] = alpha[i, j]
    return pygame.image.frombuffer(inverted_array, (w, h), 'RGBA')

# ---------------------------------------------------------

cpdef color_reduction24_c(surface_, int factor):
    """
    http://help.corel.com/paintshop-pro/v20/main/en/documentation/index.html#page/
    Corel_PaintShop_Pro%2FUnderstanding_color_reduction.html%23ww998934
    Error Diffusion — replaces the original color of a pixel with the most similar color in the palette,
    but spreads the discrepancy between the original and new colors to the surrounding pixels.
    As it replaces a color (working from the top left to the bottom right of the image),
    it adds the “error,” or discrepancy, to the next pixel, before selecting the most similar color.
    This method produces a natural-looking image and often works well for photos or complex graphics.
    With the Error Diffusion method, you select the Floyd-Steinberg, Burkes, or Stucki algorithm for
    the dithering pattern.
    :param surface_: Surface 8, 24-32 bit format (alpha transparency will be ignored).
    :param factor: integer, Number of possible color 2^n
    :return : Returns an image with color reduction using error diffusion method.
    The final image will be stripped out of its alpha channel.
    """

    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)

    if factor < 0:
        raise ValueError("\nArgument factor cannot be < 0")

    cdef int color_number = pow(2, factor)

    cdef int w, h
    w, h = surface_.get_size()

    try:
        rgb_ = pixels3d(surface_)

    except (pygame.error, ValueError):
            # unsupported colormasks for alpha reference array
            raise ValueError('\nIncompatible pixel format.')
    cdef:
        float [:, :, :] rgb_array = rgb_.astype(float32)
        unsigned char [:, :, ::1] reduce = zeros((h, w, 3), uint8, order='C')
        int x=0, y=0
        float ONE_255 = 1.0 / 255.0
        float f = 255.0 / color_number

        float new_red, new_green, new_blue
        float oldr, oldg, oldb

    with nogil:
        for y in prange(h, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for x in range(0, w):

                oldr = rgb_array[x, y, 0]
                oldg = rgb_array[x, y, 1]
                oldb = rgb_array[x, y, 2]

                new_red = round(<float>color_number * <float>oldr * ONE_255) * f
                new_green = round(<float>color_number * <float>oldg * ONE_255) * f
                new_blue = round(<float>color_number * <float>oldb *ONE_255) * f

                reduce[y, x, 0] = <unsigned char>new_red
                reduce[y, x, 1] = <unsigned char>new_green
                reduce[y, x, 2] = <unsigned char>new_blue

    return pygame.image.frombuffer(reduce, (w, h), 'RGB')


cpdef color_reduction32_c(surface_:Surface, int factor):
    """
    http://help.corel.com/paintshop-pro/v20/main/en/documentation/index.html#page/
    Corel_PaintShop_Pro%2FUnderstanding_color_reduction.html%23ww998934
    Error Diffusion — replaces the original color of a pixel with the most similar color in the palette,
    but spreads the discrepancy between the original and new colors to the surrounding pixels.
    As it replaces a color (working from the top left to the bottom right of the image),
    it adds the “error,” or discrepancy, to the next pixel, before selecting the most similar color.
    This method produces a natural-looking image and often works well for photos or complex graphics.
    With the Error Diffusion method, you select the Floyd-Steinberg, Burkes, or Stucki algorithm for
    the dithering pattern.
    :param surface_: Surface 8, 24-32 bit format (with alpha transparency).
    :param factor: integer, Number of possible color 2^n
    :return : Returns an image with color reduction using error diffusion method.
    The final image will have per-pixel transparency 
    """

    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)

    if factor < 0:
        raise ValueError("\nArgument factor cannot be < 0")

    cdef int color_number = pow(2, factor)

    cdef int w, h
    w, h = surface_.get_size()

    try:
        rgb_ = pixels3d(surface_)
        alpha_ = pixels_alpha(surface_)

    except (pygame.error, ValueError):
            # unsupported colormasks for alpha reference array
            raise ValueError('\nIncompatible pixel format.')
    cdef:
        float [:, :, :] rgb_array = rgb_.astype(float32)
        unsigned char [:, :] alpha = alpha_
        unsigned char [:, :, :] reduce = zeros((h, w, 4), uint8)
        int x=0, y=0

        float new_red, new_green, new_blue
        float oldr, oldg, oldb
        float ONE_255 = 1.0 / 255.0
        float f = 255.0 / color_number

    with nogil:
        for y in prange(0, h, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for x in range(0, w):
                oldr = rgb_array[x, y, 0]
                oldg = rgb_array[x, y, 1]
                oldb = rgb_array[x, y, 2]

                new_red = round(<float>color_number * <float>oldr * ONE_255) * f
                new_green = round(<float>color_number * <float>oldg * ONE_255) * f
                new_blue = round(<float>color_number * <float>oldb *ONE_255) * f

                reduce[y, x, 0] = <unsigned char>new_red
                reduce[y, x, 1] = <unsigned char>new_green
                reduce[y, x, 2] = <unsigned char>new_blue
                reduce[y, x, 3] = alpha[x, y]

    return pygame.image.frombuffer(reduce, (h, w), 'RGBA')


cpdef dithering24_c(surface_, int factor):
    """
    Dithering is used in computer graphics to create the illusion of "color depth" in images with
    a limited color palette - a technique also known as color quantization. In a dithered image,
    colors that are not available in the palette are approximated by a diffusion of colored pixels
    from within the available palette. The human eye perceives the diffusion as a mixture of the colors
    within it (see color vision). Dithered images, particularly those with relatively few colors,
    can often be distinguished by a characteristic graininess or speckled appearance.
    
    :param surface_: Surface 8,24-32 bit format
    :param f : integer, factor for reducing the amount of colors. f = 1 (2 colors), f = 2, (8 colors)
    :return : a dithered Surface same format than original image (no alpha channel).
    """

    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)

    cdef int w, h
    w, h = surface_.get_size()

    if factor < 0:
        raise ValueError("\nArgument factor cannot be < 0")

    cdef int color_number = pow(2, factor)

    try:
        rgb_ = pixels3d(surface_)

    except (pygame.error, ValueError):
            # unsupported colormasks for alpha reference array
            raise ValueError('\nIncompatible pixel format.')
    cdef:
        float [:, :, :] rgb_array = rgb_.astype(float32)
        float [:, :, :] new_array = zeros((w, h, 3), float32)
        int x=0, y=0

        float new_red, new_green, new_blue
        float quant_error_red, quant_error_green, quant_error_blue
        float c1 = 7.0/16.0
        float c2 = 3.0/16.0
        float c3 = 5.0/16.0
        float c4 = 1.0/16.0
        float oldr, oldg, oldb
        float ONE_255 = 1.0 / 255.0

    with nogil:
        for y in prange(1, h-1, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for x in range(1, w-1):


                oldr = <float>rgb_array[x, y, 0]
                oldg = <float>rgb_array[x, y, 1]
                oldb = <float>rgb_array[x, y, 2]

                new_red = round(<float>color_number * oldr * ONE_255) * (255.0 / <float>color_number)
                new_green = round(<float>color_number * oldg * ONE_255) * (255.0 / <float>color_number)
                new_blue = round(<float>color_number * oldb * ONE_255) * (255.0 / <float>color_number)

                rgb_array[x, y, 0], rgb_array[x, y, 1], rgb_array[x, y, 2] = new_red, new_green, new_blue

                quant_error_red = oldr - new_red
                quant_error_green = oldg - new_green
                quant_error_blue = oldb - new_blue

                rgb_array[x + 1, y, 0] = rgb_array[x + 1, y, 0] + quant_error_red * c1
                rgb_array[x + 1, y, 1] = rgb_array[x + 1, y, 1] + quant_error_green * c1
                rgb_array[x + 1, y, 2] = rgb_array[x + 1, y, 2] + quant_error_blue * c1

                rgb_array[x - 1, y + 1, 0] = rgb_array[x - 1, y + 1, 0] + quant_error_red * c2
                rgb_array[x - 1, y + 1, 1] = rgb_array[x - 1, y + 1, 1] + quant_error_green * c2
                rgb_array[x - 1, y + 1, 2] = rgb_array[x - 1, y + 1, 2] + quant_error_blue * c2

                rgb_array[x, y + 1, 0] = rgb_array[x, y + 1, 0] + quant_error_red * c3
                rgb_array[x, y + 1, 1] = rgb_array[x, y + 1, 1] + quant_error_green * c3
                rgb_array[x, y + 1, 2] = rgb_array[x, y + 1, 2] + quant_error_blue * c3

                rgb_array[x + 1, y + 1, 0] = rgb_array[x + 1, y + 1, 0] + quant_error_red * c4
                rgb_array[x + 1, y + 1, 1] = rgb_array[x + 1, y + 1, 1] + quant_error_green * c4
                rgb_array[x + 1, y + 1, 2] = rgb_array[x + 1, y + 1, 2] + quant_error_blue * c4


    return pygame.surfarray.make_surface(asarray(rgb_array, dtype=uint8))



@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef dithering32_c(surface_:Surface, int factor):
    """
    Dithering is used in computer graphics to create the illusion of "color depth" in images with
    a limited color palette - a technique also known as color quantization. In a dithered image,
    colors that are not available in the palette are approximated by a diffusion of colored pixels
    from within the available palette. The human eye perceives the diffusion as a mixture of the colors
    within it (see color vision). Dithered images, particularly those with relatively few colors,
    can often be distinguished by a characteristic graininess or speckled appearance.
    
    :param surface_: Surface 8,24-32 bit format with alpha transparency
    :param factor : integer, factor for reducing the amount of colors. factor = 1 (2 colors), factor = 2, (8 colors)
    :return : a dithered Surface same format than original image with alpha transparency.
    """

    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)

    if factor < 0:
        raise ValueError("\nArgument factor cannot be < 0")

    cdef int color_number = pow(2, factor)

    cdef int w, h
    w, h = surface_.get_size()

    try:
        rgb_ = pixels3d(surface_)
        alpha_ = pixels_alpha(surface_)

    except (pygame.error, ValueError):
            # unsupported colormasks for alpha reference array
            raise ValueError('\nIncompatible pixel format.')
    cdef:
        float [:, :, :] rgb_array = rgb_.astype(float32)
        float[:, :, :] rgba_array = zeros((h, w, 4), float32)
        unsigned char [:, :] alpha = alpha_
        int x=0, y=0

        float new_red, new_green, new_blue
        float quant_error_red, quant_error_green, quant_error_blue
        float c1 = 7.0/16.0
        float c2 = 3.0/16.0
        float c3 = 5.0/16.0
        float c4 = 1.0/16.0
        float oldr, oldg, oldb
        float ONE_255 = 1.0 / 255.0
        float f = 255.0 / color_number

    with nogil:
        for y in prange(1, h - 1, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for x in range(1, w - 1):
                oldr = <float>rgb_array[x, y, 0]
                oldg = <float>rgb_array[x, y, 1]
                oldb = <float>rgb_array[x, y, 2]

                new_red = round(color_number * oldr * ONE_255) * f
                new_green = round(color_number * oldg * ONE_255) * f
                new_blue = round(color_number * oldb * ONE_255) * f

                rgb_array[x, y, 0], rgb_array[x, y, 1], rgb_array[x, y, 2] = new_red, new_green, new_blue
                quant_error_red = oldr - new_red
                quant_error_green = oldg - new_green
                quant_error_blue = oldb - new_blue

                rgba_array[y + 1, x, 0] = <float>(rgb_array[x + 1, y, 0] + quant_error_red * c1)
                rgba_array[y + 1, x, 1] = <float>(rgb_array[x + 1, y, 1] + quant_error_green * c1)
                rgba_array[y + 1, x, 2] = <float>(rgb_array[x + 1, y, 2] + quant_error_blue * c1)

                rgba_array[y - 1, x + 1, 0] = <float>(rgb_array[x - 1, y + 1, 0] + quant_error_red * c2)
                rgba_array[y - 1, x + 1, 1] = <float>(rgb_array[x - 1, y + 1, 1] + quant_error_green * c2)
                rgba_array[y - 1, x + 1, 2] = <float>(rgb_array[x - 1, y + 1, 2] + quant_error_blue * c2)

                rgba_array[y, x + 1, 0] = <float>(rgb_array[x, y + 1, 0] + quant_error_red * c3)
                rgba_array[y, x + 1, 1] = <float>(rgb_array[x, y + 1, 1] + quant_error_green * c3)
                rgba_array[y, x + 1, 2] = <float>(rgb_array[x, y + 1, 2] + quant_error_blue * c3)

                rgba_array[y + 1, x + 1, 0] = <float>(rgb_array[x + 1, y + 1, 0] + quant_error_red * c4)
                rgba_array[y + 1, x + 1, 1] = <float>(rgb_array[x + 1, y + 1, 1] + quant_error_green * c4)
                rgba_array[y + 1, x + 1, 2] = <float>(rgb_array[x + 1, y + 1, 2] + quant_error_blue * c4)

                rgba_array[y, x, 3] = <float>alpha[x, y]

    return pygame.image.frombuffer(asarray(rgba_array, dtype=uint8), (h, w), 'RGBA')


cdef double distance_ (double x1, double y1, double x2, double y2)nogil:

  return sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2));


cdef double gaussian_ (double v, double sigma)nogil:

  return (1.0 / (2.0 * 3.14159265358 * (sigma * sigma))) * exp(-(v * v ) / (2.0 * sigma * sigma))


cpdef bilateral_filter24_c(image: Surface, double sigma_s, double sigma_i):
    """
    A bilateral filter is a non-linear, edge-preserving, and noise-reducing
    smoothing filter for images. It replaces the intensity of each pixel with a
    weighted average of intensity values from nearby pixels. This weight can be
    based on a Gaussian distribution.

    :param image: Surface 8, 24-32 bit format (alpha channel will be ignored)
    :param sigma_s: float sigma_s : Spatial extent of the kernel, size of the considered neighborhood. 
    Value of sigma in the color space. The greater the value, the colors farther to each other will start to get mixed.
    :param sigma_i: float sigma_i range kernel, minimum amplitude of an edge.Value of \sigma in the coordinate space. 
    The greater its value, the more further pixels will mix together, given that their colors lie within the 
    sigmaColor range.
    :return: return a filtered Surface
    """
    # todo check sigma for division by zeros
    assert isinstance(image, Surface), \
        'Argument image must be a valid Surface, got %s ' % type(image)

    # texture sizes
    cdef int w, h
    w, h = image.get_size()

    try:
        array_ = pixels3d(image)

    except (pygame.error, ValueError):
        raise ValueError('\nTexture/image is not compatible.')

    assert w != 0 or h !=0,\
            'image with incorrect dimensions (w>0, h>0) got (%s, %s) ' % (w, h)
    cdef:
        unsigned char [:, :, :] rgb_array = array_
        unsigned char [:, :, ::1] bilateral = zeros((h, w, 3), order='C', dtype=uint8)
        int x, y, xx, yy
        int k = 4
        int kx, ky
        double gs, wr, wg, wb, ir, ig, ib , wpr, wpg, wpb
        int w_1 = w
        int h_1 = h


    with nogil:

        for x in prange(0, w_1, schedule=SCHEDULE, num_threads=THREAD_NUMBER):

            for y in range(0, h_1):

                ir, ig, ib = 0, 0, 0
                wpr, wpg, wpb = 0, 0, 0

                for ky in range(-k, k + 1):
                    for kx in range(-k, k + 1):

                        xx = x + kx
                        yy = y + ky

                        if xx < 0:
                            xx = 0
                        elif xx > w_1:
                            xx = w_1
                        if yy < 0:
                            yy = 0
                        elif yy > h_1:
                            yy = h_1
                        gs = gaussian_(distance_(xx, yy, x, y), sigma_s)

                        wr = gaussian_(rgb_array[xx, yy, 0] - rgb_array[x, y, 0], sigma_i) * gs
                        wg = gaussian_(rgb_array[xx, yy, 1] - rgb_array[x, y, 1], sigma_i) * gs
                        wb = gaussian_(rgb_array[xx, yy, 2] - rgb_array[x, y, 2], sigma_i) * gs
                        ir = ir + rgb_array[xx, yy, 0] * wr
                        ig = ig + rgb_array[xx, yy, 1] * wg
                        ib = ib + rgb_array[xx, yy, 2] * wb
                        wpr = wpr + wr
                        wpg = wpg + wg
                        wpb = wpb + wb
                ir = ir / wpr
                ig = ig / wpg
                ib = ib / wpb
                bilateral[y, x, 0], bilateral[y, x, 1], bilateral[y, x, 2] = \
                             <unsigned char>(round(ir)), <unsigned char>(round(ig)), <unsigned char>(round(ib))

    return pygame.image.frombuffer(bilateral, (w, h), 'RGB')



cpdef median_filter24_c(image, int kernel_size):
    """
    :param image: Surface 8. 24-32 bit 
    :param kernel_size: Kernel width 
    """

    assert isinstance(image, Surface), \
            'Argument image must be a valid Surface, got %s ' % type(image)

    cdef int w, h
    w, h = image.get_size()

    try:
        array_ = pixels3d(image)
    except (pygame.error, ValueError):
        raise ValueError('\nTexture/image is not compatible.')

    assert w != 0 or h !=0,\
            'image with incorrect dimensions (w>0, h>0) got (%s, %s) ' % (w, h)
    cdef:
        unsigned char [:, :, :] rgb_array = array_
        unsigned char [:, :, ::1] median_array = zeros((w, h, 3), dtype=uint8, order='C')
        int i=0, j=0, ky, kx, ii=0, jj=0
        int k = kernel_size >> 1
        int k_size = kernel_size * kernel_size

        int *tmp_red   = <int *> malloc(k_size * sizeof(int))
        int *tmp_green = <int *> malloc(k_size * sizeof(int))
        int *tmp_blue  = <int *> malloc(k_size * sizeof(int))
        int *tmpr
        int *tmpg
        int *tmpb

        int index = 0
        int w_1 = w, h_1 = h

    with nogil:
        for i in prange(0, w_1, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(0, h_1):

                index = 0

                for kx in range(-k, k):
                    for ky in range(-k, k):

                        ii = i + kx
                        jj = j + ky

                        if ii < 0:
                            ii = 0
                        elif ii > w:
                            ii = w

                        if jj < 0:
                            jj = 0
                        elif jj > h:
                            jj = h

                        # add values to the memoryviews
                        tmp_red[index] = rgb_array[ii, jj, 0]
                        tmp_green[index] = rgb_array[ii, jj, 1]
                        tmp_blue[index] = rgb_array[ii, jj, 2]
                        index = index + 1

                median_array[i, j, 0]=tmp_red[k + 1]
                median_array[i, j, 1]=tmp_green[k + 1]
                median_array[i, j, 2]=tmp_blue[k + 1]

                # External C quicksort
                tmpr = quickSort(tmp_red, 0, k_size)
                tmpg = quickSort(tmp_green, 0, k_size)
                tmpb = quickSort(tmp_blue, 0, k_size)
                median_array[i, j, 0] = tmpr[k + 1]
                median_array[i, j, 1] = tmpg[k + 1]
                median_array[i, j, 2] = tmpb[k + 1]

    return pygame.surfarray.make_surface(asarray(median_array))




cpdef median_filter32_c(image, int kernel_size):
    """
    :param image: Surface 8. 24-32 bit with per-pixel transparency
    :param kernel_size: Kernel width e.g 3 for a matrix 3 x 3
    :return: Returns a Surface with no alpha channel
    """

    assert isinstance(image, Surface), \
            'Argument image must be a valid Surface, got %s ' % type(image)

    cdef int w, h
    w, h = image.get_size()

    try:
        array_ = pixels3d(image)
        alpha_ = pixels_alpha(image)

    except (pygame.error, ValueError):
        raise ValueError('\nTexture/image is not compatible.')

    assert w != 0 or h !=0,\
            'image with incorrect dimensions (w>0, h>0) got (%s, %s) ' % (w, h)
    cdef:
        unsigned char [:, :, :] rgb_array = array_
        unsigned char [:, :] alpha = alpha_
        unsigned char [:, :, ::1] median_array = zeros((h, w, 4), dtype=uint8, order='C')
        int i=0, j=0, ky, kx, ii=0, jj=0
        int k = kernel_size >> 1
        int k_size = kernel_size * kernel_size

        int *tmp_red   = <int *> malloc(k_size * sizeof(int))
        int *tmp_green = <int *> malloc(k_size * sizeof(int))
        int *tmp_blue  = <int *> malloc(k_size * sizeof(int))
        int *tmpr
        int *tmpg
        int *tmpb
        int index = 0


    with nogil:

        for i in prange(0, w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(0, h):

                index = 0

                for kx in range(-k, k):
                    for ky in range(-k, k):
                        ii = i + kx
                        jj = j + ky
                        # substitute the pixel is close to the edge.
                        # below zero, pixel will be pixel[0], over w, pixel will
                        # be pixel[w]
                        if ii < 0:
                            ii = 0
                        elif ii > w:
                            ii = w

                        if jj < 0:
                            jj = 0
                        elif jj > h:
                            jj = h

                        # add values to the memoryviews
                        tmp_red[index] = rgb_array[ii, jj, 0]
                        tmp_green[index] = rgb_array[ii, jj, 1]
                        tmp_blue[index] = rgb_array[ii, jj, 2]
                        index = index + 1

                # External C quicksort
                tmpr = quickSort(tmp_red, 0, k_size)
                tmpg = quickSort(tmp_green, 0, k_size)
                tmpb = quickSort(tmp_blue, 0, k_size)
                median_array[j, i, 0] = tmpr[k + 1]
                median_array[j, i, 1] = tmpg[k + 1]
                median_array[j, i, 2] = tmpb[k + 1]
                median_array[j, i, 3] = alpha[i, j]

    return pygame.image.frombuffer(median_array, (w, h), 'RGBA')



cpdef greyscale_lightness24_c(image):
    """
    Transform a pygame surface into a greyscale (conserve lightness).
    Compatible with 8, 24-32 bit format image with or without
    alpha channel.
    greyscale formula lightness = (max(RGB) + min(RGB))//2

    EXAMPLE:
        im1 = pygame.image.load('path to your image here')
        output = greyscale_light(im1)   

    :param image: pygame surface 8, 24-32 bit format 
    :return: a greyscale Surface without alpha channel 24-bit

    """

    assert isinstance(image, Surface),\
        'Argument image is not a valid Surface got %s ' % type(image)

    try:
        array_ = pixels3d(image)
    except (pygame.error, ValueError):
        raise ValueError('Incompatible image.')

    # acquires a buffer object for the pixels of the Surface.
    cdef int w_, h_
    w_, h_ = image.get_size()

    if w_==0 or h_==0:
        raise ValueError('Image with incorrect dimensions, must be (w>0, h>0) got (w:%s, h:%s) ' % (w_, h_))

    cdef:
        int w = w_, h = h_
        unsigned char[:, :, :] rgb_array = array_                           # non-contiguous values
        unsigned char[:, :, ::1] rgb_out = empty((h, w, 3), dtype=uint8)    # contiguous values
        int red, green, blue, grey, lightness
        int i=0, j=0

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                red, green, blue = rgb_array[i, j, 0], rgb_array[i, j, 1], rgb_array[i, j, 2]
                lightness = (max(red, green, blue) + min(red, green, blue)) >> 1
                rgb_out[j, i, 0], rgb_out[j, i, 1], rgb_out[j, i, 2] =  lightness, lightness, lightness

    return pygame.image.frombuffer(rgb_out, (w, h), 'RGB')


cpdef greyscale_lightness32_c(image):
    """
    Transform an image into greyscale (conserve lightness).

    The image must have per-pixel information
    greyscale formula lightness = (max(RGB) + min(RGB))//2

    EXAMPLE:
        im1 = pygame.image.load('path to your image here')
        output = greyscale_light_alpha(im1)   

    :param image: pygame 32-bit format surface (image must have per-pixel information or,
    needs to be converted with pygame methods convert_alpha() 
    :return: Return Greyscale Surface 32-bit with alpha channel.

    """
    assert isinstance(image, Surface), \
        'Argument image is not a valid Surface got %s ' % type(image)

    # Image must be 32-bit format and must have per-pixel transparency
    if not ((image.get_bitsize() == 32) and bool(image.get_flags() & pygame.SRCALPHA)):
        raise ValueError('Surface without per-pixel information.')

    try:
        array_ = pixels3d(image)
        alpha_ = pixels_alpha(image)
    except (pygame.error, ValueError):
        raise ValueError('Incompatible image.')

    cdef:
        unsigned char [:, :, :] pixels = array_  # non-contiguous values
        unsigned char [:, :] alpha = alpha_    # contiguous values
        int w, h

    w, h = image.get_size()
    if w==0 or h==0:
        raise ValueError('Image with incorrect dimensions, must be (w>0, h>0) got (w:%s, h:%s) ' % (w, h))

    cdef:
        unsigned char [:, :, ::1] grey_c = empty((h, w, 4), dtype=uint8)  # contiguous values
        int i=0, j=0, lightness
        unsigned char r, g, b

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r = pixels[i, j, 0]
                g = pixels[i, j, 1]
                b = pixels[i, j, 2]
                lightness = (<int>(max_rgb_value(r, g, b) + min_rgb_value(r, g, b))) >> 1
                grey_c[j, i, 0] = lightness
                grey_c[j, i, 1] = lightness
                grey_c[j, i, 2] = lightness
                grey_c[j, i, 3] = alpha[i, j]

    return pygame.image.frombuffer(grey_c, (w, h), 'RGBA')


cpdef greyscale_luminosity32_c(surface_):
    """
    Transform an image into greyscale (conserve luminosity)
    The image must have per-pixel information otherwise
    a ValueError will be raised 

    greyscale formula luminosity = R * 0.2126, G * 0.7152, B * 0.0722

    EXAMPLE:
        im1 = pygame.image.load('path to your image here')
        output = greyscale_lum_alpha(im1)   

    :param surface_: pygame surface with alpha channel 
    :return: Return Greyscale 32-bit surface with alpha channel 

    """

    assert isinstance(surface_, Surface), 'Argument image is not a valid Surface got %s ' % type(surface_)

    try:
        array_ = pixels3d(surface_)
    except (pygame.error, ValueError):
        raise ValueError('Incompatible image.')

    try:
        alpha_ = pixels_alpha(surface_)
    except (pygame.error, ValueError):
        raise ValueError('Surface without per-pixel information.')


    cdef:
        unsigned char [:, :, :] pixels = array_ # non-contiguous values
        unsigned char [:, :] alpha = alpha_   # not contiguous
        int w, h

    w, h = surface_.get_size()
    if w==0 or h==0:
        raise ValueError('Image with incorrect dimensions, must be (w>0, h>0) got (w:%s, h:%s) ' % (w, h))

    cdef:
        unsigned char [:, :, ::1] grey_c = empty((h, w, 4), dtype=uint8)    # contiguous values
        int i=0, j=0, luminosity
        unsigned char r, g, b

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                r = pixels[i, j, 0]
                g = pixels[i, j, 1]
                b = pixels[i, j, 2]
                luminosity = <unsigned char>(r * 0.2126 + g * 0.7152 + b * 0.072)
                grey_c[j, i, 0], grey_c[j, i, 1], grey_c[j, i, 2], \
                    grey_c[j, i, 3] = luminosity, luminosity, luminosity, alpha[i, j]

    return pygame.image.frombuffer(grey_c, (w, h), 'RGBA')


cpdef greyscale_luminosity24_c(surface_):
    """
    Transform a Surface into a greyscale (conserve lightness).
    Compatible with 8, 24-32 bit format image with or without
    alpha channel.

    greyscale formula luminosity = R * 0.2126, G * 0.7152, B * 0.0722

    EXAMPLE:
        im1 = pygame.image.load('path to your image here')
        output = greyscale_lum(im1)   

    :param surface_: Surface 8, 24-32 bit format
    :return: Returns a greyscale 24-bit Surface without alpha channel

    """

    assert isinstance(surface_, Surface), 'Argument image is not a valid Surface got %s ' % type(surface_)

    try:
        array_ = pixels3d(surface_)

    except (pygame.error, ValueError):
        raise ValueError('Incompatible image.')

    cdef int w_, h_
    w_, h_ = surface_.get_size()

    if w_==0 or h_==0:
        raise ValueError('Image with incorrect dimensions, '
                         'must be (w>0, h>0) got (w:%s, h:%s) ' % (w_, h_))

    cdef:
        int w = w_, h = h_
        unsigned char[:, :, :] rgb_array = array_                           # non-contiguous values
        unsigned char[:, :, ::1] rgb_out = empty((h, w, 3), dtype=uint8)    # contiguous values
        int red, green, blue, grey, luminosity
        int i=0, j=0

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                red, green, blue = rgb_array[i, j, 0], rgb_array[i, j, 1], rgb_array[i, j, 2]
                luminosity = <unsigned char>(red * 0.2126 + green * 0.7152 +  blue * 0.0722)
                rgb_out[j, i, 0], rgb_out[j, i, 1], rgb_out[j, i, 2] =  luminosity, luminosity, luminosity

    return pygame.image.frombuffer(rgb_out, (w, h), 'RGB')

cpdef greyscale32_c(surface_):
    """
    Transform an image into greyscale.
    The image must have per-pixel information encoded otherwise
    a ValueError will be raised 

    EXAMPLE:
        im1 = pygame.image.load('path to your image here')
        output = make_greyscale_32(im1)  

    :param surface_: pygame surface with alpha channel 
    :return: Return Greyscale 32-bit Surface with alpha channel 

    """

    assert isinstance(surface_, Surface), 'Argument image is not a valid Surface got %s ' % type(surface_)

    try:
        array_ = pixels3d(surface_)
    except (pygame.error, ValueError):
        raise ValueError('Incompatible image.')

    try:
        alpha_ = pixels_alpha(surface_)
    except (pygame.error, ValueError):
        raise ValueError('Surface without per-pixel information.')

    cdef:
        unsigned char [:, :, :] pixels = array_ # non-contiguous values
        unsigned char [:, :] alpha = alpha_     # contiguous values
        int w, h

    w, h = surface_.get_size()

    if w==0 or h==0:
        raise ValueError('Image with incorrect dimensions, must be (w>0, h>0) got (w:%s, h:%s) ' % (w, h))

    cdef:
        unsigned char [:, :, ::1] grey_c = empty((h, w, 4), dtype=uint8)    # contiguous values
        int i=0, j=0
        unsigned char grey_value
        double c1 = 1.0/3.0
    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                grey_value = <unsigned char>((pixels[i, j, 0] + pixels[i, j, 1] + pixels[i, j, 2]) * c1)
                grey_c[j, i, 0], grey_c[j, i, 1], grey_c[j, i, 2], \
                    grey_c[j, i, 3] = grey_value, grey_value, grey_value, 255 # alpha[i, j]

    return pygame.image.frombuffer(grey_c, (w, h), 'RGBA')


cpdef greyscale24_c(surface_):
    """
    Transform a pygame surface into a greyscale.
    Compatible with 8, 24-32 bit format image with or without
    alpha channel.

    EXAMPLE:
        im1 = pygame.image.load('path to your image here')
        output = make_greyscale_24(im1)  

    :param surface_: pygame surface 8, 24-32 bit format
    :return: Returns a greyscale 24-bit surface without alpha channel

    """

    assert isinstance(surface_, Surface), 'Argument image is not a valid Surface got %s ' % type(surface_)

    try:
        array_ = pixels3d(surface_)
    except (pygame.error, ValueError):
        raise ValueError('Incompatible image.')

    cdef int w_, h_
    # acquires a buffer object for the pixels of the Surface.
    w_, h_ = surface_.get_size()

    if w_==0 or h_==0:
        raise ValueError('Image with incorrect dimensions, '
                         'must be (w>0, h>0) got (w:%s, h:%s) ' % (w_, h_))
    cdef:
        int w = w_, h = h_
        unsigned char[:, :, :] rgb_array = array_                        # non-contiguous
        unsigned char[:, :, ::1] rgb_out = empty((h, w, 3), dtype=uint8) # contiguous
        int red, green, blue, grey
        int i=0, j=0

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                red, green, blue = rgb_array[i, j, 0], rgb_array[i, j, 1], rgb_array[i, j, 2]
                grey = <int>((red + green + blue) * 0.33)
                rgb_out[j, i, 0], rgb_out[j, i, 1], rgb_out[j, i, 2] =  grey, grey, grey

    return pygame.image.frombuffer(rgb_out, (w, h), 'RGB')



cpdef sobel24(surface_, float threshold=20.0):
    """
    The Sobel operator, sometimes called the Sobel–Feldman operator or Sobel filter,
    is used in image processing and computer vision, particularly within edge detection 
    algorithms where it creates an image emphasising edges. 
    
    :param surface_: pygame.Surface format 24-bit or 32 bit 
    :param threshold: float; represent the edge detection threshold range [0.0 ... 255.0] default 20.0
    :return: Return a numpy.ndarray format (w x h x 3) uint8 (unsigned char)
    """

    assert isinstance(surface_, Surface), \
        'Argument image must be a valid Surface, got %s ' % type(surface_)

    cdef int w, h
    w, h = surface_.get_size()

    cdef unsigned char [:, :, :] rgb_array

    try:
        rgb_array = pixels3d(surface_)
    except:
        raise ValueError("Surface is not a valid 24, 32-bit pygame surface")

    cdef:
        short [:, :] gy = numpy.array(
            ([-1, 0, 1],
             [-2, 0, 2],
             [-1, 0, 1])).astype(dtype=int16, order='C')

        short [:, :] gx = numpy.array(
            ([-1, -2, -1],
             [0,   0,  0],
             [1,   2,  1])).astype(dtype=int16, order='c')

        unsigned short int kernel_half = 1
        # kernel length
        unsigned short int k_length = len(gx)
        unsigned short int half_kernel = k_length >> 1
        int kernel_offset_x, kernel_offset_y
        float [:, :, :] source_array = numpy.empty((w, h, 3), dtype=float32)
        int x, y, xx, yy, k
        float r_gx, r_gy
        unsigned char gray=0
        float magnitude


    with nogil:

        for y in prange(0, w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):

            for x in range(0, h):

                r_gx, r_gy = 0.0, 0.0

                for kernel_offset_y in range(-kernel_half, kernel_half + 1):

                    for kernel_offset_x in range(-kernel_half, kernel_half + 1):

                        xx = x + kernel_offset_x
                        yy = y + kernel_offset_y

                        if xx > h - 1:
                            xx = h - 1
                        if xx < 0:
                            xx = 0

                        if yy > w - 1:
                            yy = w - 1
                        if yy < 0:
                            yy = 0

                        # grayscale image red = green = blue
                        gray = rgb_array[xx, yy, 0]

                        if kernel_offset_x != 0:
                            k = gx[kernel_offset_x + kernel_half, kernel_offset_y + kernel_half]
                            r_gx = r_gx + <float>gray * <float>k

                        if kernel_offset_y != 0:
                            k = gy[kernel_offset_x + kernel_half, kernel_offset_y + kernel_half]
                            r_gy = r_gy + <float>gray * <float>k

                magnitude = <float>sqrt(r_gx * r_gx + r_gy * r_gy)
                if magnitude > 255:
                    magnitude = 255.0

                # update the pixel if the magnitude is above threshold else black pixel
                source_array[x, y] = magnitude if magnitude > threshold else 0

    return asarray(source_array).astype(dtype=uint8)


cpdef sobel32(surface_, float threshold=20.0):
    """
    The Sobel operator, sometimes called the Sobel–Feldman operator or Sobel filter,
    is used in image processing and computer vision, particularly within edge detection 
    algorithms where it creates an image emphasising edges. 

    :param surface_: pygame.Surface format 24-bit or 32 bit 
    :param threshold: float; represent the edge detection threshold range [0.0 ... 255.0] default 20.0
    :return: Return a numpy.ndarray format (w x h x 3) uint8 (unsigned char)
    """

    assert isinstance(surface_, Surface), \
        'Argument image must be a valid Surface, got %s ' % type(surface_)

    cdef int w, h
    w, h = surface_.get_size()

    cdef unsigned char [:, :, :] rgb_array
    cdef unsigned char [:, :] alpha
    try:
        rgb_array = pixels3d(surface_)
        alpha = array_alpha(surface_)
    except:
        raise ValueError("Surface is not a valid 24, 32-bit pygame surface")

    cdef:
        short [:, :] gy = numpy.array(
            ([-1, 0, 1],
             [-2, 0, 2],
             [-1, 0, 1])).astype(dtype=int16, order='C')

        short [:, :] gx = numpy.array(
            ([-1, -2, -1],
             [0,   0,  0],
             [1,   2,  1])).astype(dtype=int16, order='c')

        unsigned short int kernel_half = 1
        # kernel length
        unsigned short int k_length = len(gx)
        unsigned short int half_kernel = k_length >> 1
        int kernel_offset_x, kernel_offset_y
        unsigned char [:, :, :] source_array = numpy.empty((h, w, 4), dtype=uint8)
        int x, y, xx, yy, k
        float r_gx, r_gy
        unsigned char gray=0
        float magnitude


    with nogil:
        for x in prange(0, w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):

            for y in range(0, h):

                r_gx, r_gy = 0.0, 0.0

                for kernel_offset_y in range(-kernel_half, kernel_half + 1):

                    for kernel_offset_x in range(-kernel_half, kernel_half + 1):

                        xx = x + kernel_offset_x
                        yy = y + kernel_offset_y

                        if xx > w - 1:
                            xx = w - 1
                        if xx < 0:
                            xx = 0

                        if yy > h - 1:
                            yy = h - 1
                        if yy < 0:
                            yy = 0

                        # grayscale image red = green = blue
                        gray = rgb_array[xx, yy, 0]

                        if kernel_offset_x != 0:
                            k = gx[kernel_offset_x + kernel_half, kernel_offset_y + kernel_half]
                            r_gx = r_gx + <float>gray * <float>k

                        if kernel_offset_y != 0:
                            k = gy[kernel_offset_x + kernel_half, kernel_offset_y + kernel_half]
                            r_gy = r_gy + <float>gray * <float>k

                magnitude = <float>sqrt(r_gx * r_gx + r_gy * r_gy)
                if magnitude > 255:
                    magnitude = 255.0

                # update the pixel if the magnitude is above threshold else black pixel
                source_array[y, x, 0] = <unsigned char>magnitude if magnitude > threshold else 0
                source_array[y, x, 1] = <unsigned char>magnitude if magnitude > threshold else 0
                source_array[y, x, 2] = <unsigned char>magnitude if magnitude > threshold else 0
                source_array[y, x, 3] = alpha[xx, yy]

    return pygame.image.frombuffer(source_array, (h, w), "RGBA")


class Sobel4:
    """
    The Sobel operator, sometimes called the Sobel–Feldman operator or Sobel filter,
    is used in image processing and computer vision, particularly within edge detection
    algorithms where it creates an image emphasising edges.

    """

    def __init__(self, surface_, array_):

        self.gy = numpy.array(([-1, 0, 1],
                               [-2, 0, 2],
                               [-1, 0, 1]))
        self.gx = numpy.array(([-1, -2, -1],
                               [0, 0, 0],
                               [1, 2, 1]))

        self.kernel_half = 1
        self.surface = surface_
        self.shape = array_.shape
        self.array = array_
        self.source_array = numpy.zeros((self.shape[0], self.shape[1], 3))
        self.threshold = 70

    def run(self):

        for y in range(2, self.shape[1]-2):

            for x in range(2, self.shape[0]-2):
                r_gx, r_gy = 0, 0
                for kernel_offset_y in range(-self.kernel_half, self.kernel_half + 1):

                    for kernel_offset_x in range(-self.kernel_half, self.kernel_half + 1):

                        xx = x + kernel_offset_x
                        yy = y + kernel_offset_y
                        color = self.surface.get_at((xx, yy))

                        # print(kernel_offset_y, kernel_offset_x)
                        if kernel_offset_x != 0:

                            k = self.gx[kernel_offset_x + self.kernel_half,
                                        kernel_offset_y + self.kernel_half]
                            r_gx += color[0] * k


                        if kernel_offset_y != 0:
                            k = self.gy[kernel_offset_x + self.kernel_half,
                                        kernel_offset_y + self.kernel_half]
                            r_gy += color[0] * k


                magnitude = sqrt(r_gx * r_gx + r_gy * r_gy)

                # update the pixel if the magnitude is above threshold else black pixel
                self.source_array[x, y] = magnitude if magnitude > self.threshold else 0


        # cap the values
        numpy.putmask(self.source_array, self.source_array > 255, 255)
        numpy.putmask(self.source_array, self.source_array < 0, 0)
        return self.source_array



cdef inline unsigned char [:, :, ::1] pixel_block_rgb(
        unsigned char [:, :, :] array_, int start_x, int start_y,
        int w, int h, unsigned char [:, :, ::1] block) nogil:
    """
    EXTRACT A SPRITE FROM A SPRITE SHEET 

    * Method used by Sprite_Sheet_Uniform_RGB in order to extract all the sprites from the sprite sheet
    * This method returns a memoryview type [:, :, ::1] contiguous of unsigned char (sprite of size w x h)

    :param array_ : unsigned char; array of size w x h x 3 to parse into sub blocks (non contiguous)
    :param start_x: int; start of the block (x value) 
    :param start_y: int; start of the block (y value)
    :param w      : int; width of the block
    :param h      : int; height of the block
    :param block  : unsigned char; empty block of size w_n x h_n x 3 to fill up 
    :return       : Return 3d array of size (w_n x h_n x 3) of RGB pixels 
    """

    cdef:
        int x, y, xx, yy

    for x in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
        xx = start_x + x
        for y in range(h):
            yy = start_y + y
            block[x, y, 0] = array_[xx, yy, 0]
            block[x, y, 1] = array_[xx, yy, 1]
            block[x, y, 2] = array_[xx, yy, 2]

    return block

# NOTE : method below already exist in SpriteSheet.pyx
cdef inline unsigned char [:, :, ::1] pixel_block_rgba(
        unsigned char [:, :, :] array_, int start_x, int start_y,
        int w, int h, unsigned char [:, :, ::1] block) nogil:
    """
    EXTRACT A SPRITE FROM A SPRITE SHEET (SPRITE WITH PER PIXEL INFORMATION)

    * Method used by Sprite_Sheet_Uniform_RGBA in order to extract all the sprites from the sprite sheet
    * This method returns a memoryview type [:, :, ::1] contiguous of unsigned char (sprite of size w x h)

    :param array_ : unsigned char; array of size w x h x 4 to parse into sub blocks (non contiguous)
    :param start_x: int; start of the block (x value) 
    :param start_y: int; start of the block (y value)
    :param w      : int; width of the block
    :param h      : int; height of the block
    :param block  : unsigned char; empty block of size w_n x h_n x 4 to fill up 
    :return       : Return 3d array of size (w_n x h_n x 4) of RGBA pixels 
    """

    cdef:
        int x, y, xx, yy

    for x in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
        xx = start_x + x
        for y in prange(h, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            yy = start_y + y
            block[x, y, 0] = array_[xx, yy, 0]
            block[x, y, 1] = array_[xx, yy, 1]
            block[x, y, 2] = array_[xx, yy, 2]
            block[x, y, 3] = array_[xx, yy, 3]
    return block

cpdef create_pixel_blocks_rgba(surface_, int size_, int rows_, int columns_):
    """
    
    :param surface_: 
    :param size_: 
    :param rows_: 
    :param columns_: 
    :return: 
    """

    cdef int bitsize

    if not pygame.display.get_init():
        raise ValueError("Display module has not been initialized")


    cdef int w, h
    w, h = surface_.get_size()

    cdef:
        # rgba_array is flipped h x w
        unsigned char [:, :, :] rgba_array = pixels3d(surface_).transpose(1, 0, 2)
        list sprite_animation = []
        int rows, columns
        int start_x, end_x, start_y, end_y;
        int x=size_, y=size_
        int width=w, height=h

    if size_ == 0:
        raise ValueError("\nArgument size_ cannot be zero!")
    if width / size_ != columns_ or height / size_ != rows_:
        raise ValueError("\nAt least one arguments such as rows_, columns_ or size_ is incorrect")

    cdef:
        unsigned char [:, :, ::1] empty_array = empty((size_, size_, 4), uint8)
        unsigned char [:, :, ::1] block_array = empty((size_, size_, 4), uint8)

    with nogil:
        for rows in range(rows_):
            start_y = rows * size_
            end_y   = (rows + 1) * size_
            for columns in range(columns_):
                start_x = columns * size_
                end_x   = start_x + size_
                # start_y and start_x are swapped (rgba_array is flipped)
                block_array = pixel_block_rgba(rgba_array, start_y, start_x, x, y, empty_array)
                with gil:
                    block_array_asarray = asarray(block_array)
                    sub_surface = frombuffer(
                        block_array_asarray.copy(order='C'), (size_, size_), 'RGBA')
                    PyList_Append(sprite_animation, sub_surface.convert_alpha())
    return sprite_animation


cpdef create_pixel_blocks_rgb(surface_, int size_, int rows_, int columns_):

    cdef:
        unsigned int w, h
        int bitsize

    bitsize = surface_.get_bitsize()
    w, h = surface_.get_size()

    cdef:

        unsigned char [:, :, :] rgb_array = pixels3d(surface_).transpose(1, 0, 2)
        list subsurface = []
        int rows, columns
        int start_x, end_x, start_y, end_y;
        int width = <object>rgb_array.shape[1]
        int height = <object>rgb_array.shape[0]

    cdef:
        unsigned char [:, :, ::1] empty_array = empty((size_, size_, 3), uint8)
        unsigned char [:, :, ::1] block_array = empty((size_, size_, 3), uint8)

    with nogil:
        for rows in range(rows_):
            start_y = rows * size_
            end_y   = (rows + 1) * size_
            for columns in range(columns_):
                start_x = columns * size_
                end_x   = start_x + size_
                block_array = pixel_block_rgb(rgb_array, start_y, start_x, size_, size_, empty_array)
                with gil:
                    block_array_asarray = asarray(block_array)
                    sub_surface = frombuffer(
                        block_array_asarray.copy(order='C'), (size_, size_), 'RGB')
                    PyList_Append(subsurface, sub_surface.convert())
    return subsurface


cpdef pixelate24(surface_):

    assert isinstance(surface_, Surface), \
        'Argument image must be a valid Surface, got %s ' % type(surface_)

    cdef int w, h
    w, h = surface_.get_size()

    cdef unsigned char [:, :, :] rgb_array
    try:
        rgb_array = pixels3d(surface_)

    except:
        raise ValueError("Surface is not a valid 24, 32-bit pygame surface")

    cdef:

        unsigned char [:, :, :] source_array = numpy.empty((w, h, 3), dtype=uint8)
        int x, y
        int length = w * h
        float r=0.0, g=0.0, b=0.0

    with nogil:
        for x in prange(0, w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for y in range(0, h):
                r += rgb_array[x, y, 0]
                g += rgb_array[x, y, 1]
                b += rgb_array[x, y, 2]

        r = <float> r / <float> length
        g = <float> g / <float> length
        b = <float> b / <float> length

        for x in prange(0, w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for y in range(0, h):
                source_array[x, y, 0] = <unsigned char>r
                source_array[x, y, 1] = <unsigned char>g
                source_array[x, y, 2] = <unsigned char>b

    return pygame.surfarray.make_surface(asarray(source_array))


cpdef pixelate32(surface_):

    assert isinstance(surface_, Surface), \
        'Argument image must be a valid Surface, got %s ' % type(surface_)

    cdef int w, h
    w, h = surface_.get_size()

    cdef unsigned char [:, :, :] rgb_array
    cdef unsigned char [:, :] alpha_array
    try:
        rgb_array = pixels3d(surface_)
        alpha_array = array_alpha(surface_)

    except:
        raise ValueError("Surface is not a valid 24, 32-bit pygame surface")

    cdef:

        unsigned char [:, :, :] source_array = numpy.empty((h, w, 4), dtype=uint8)

        int x, y
        float length = w * h
        float r=0.0, g=0.0, b=0.0, a =0.0

    with nogil:
        for x in prange(0, w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for y in range(0, h):
                r += rgb_array[x, y, 0]
                g += rgb_array[x, y, 1]
                b += rgb_array[x, y, 2]
                a += alpha_array[x, y]

        r = <float> r / <float> length
        g = <float> g / <float> length
        b = <float> b / <float> length
        a = <float> a / <float> length

        for x in prange(0, w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for y in range(0, h):
                source_array[y, x, 0] = <unsigned char>r
                source_array[y, x, 1] = <unsigned char>g
                source_array[y, x, 2] = <unsigned char>b
                source_array[y, x, 3] = <unsigned char>a


    return pygame.image.frombuffer(source_array, (h, w), "RGBA")


cpdef sepia24_c(surface_):
    """
    Create a sepia image from the given Surface (compatible with 8, 24-32 bit format image)
    Alpha channel will be ignored from image converted with the pygame method convert_alpha.

    :param surface_: Surface, loaded with pygame.image method
    :return: Return a Surface in sepia ready to be display, the final image will not hold any per-pixel
    transparency layer
    """

    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)
    cdef int w, h
    w, h = surface_.get_size()

    try:
        rgb_ = pixels3d(surface_)
    except (pygame.error, ValueError):
            # unsupported colormasks for alpha reference array
            raise ValueError('\nIncompatible pixel format.')
    cdef:
        unsigned char [:, :, :] rgb_array = rgb_
        unsigned char [:, :, :] new_array = empty((h, w, 3), dtype=uint8)
        int i=0, j=0
        int r, g, b
    with nogil:
        for i in prange(w):
            for j in range(h):
                r = <int>(rgb_array[i, j, 0] * 0.393 +
                          rgb_array[i, j, 1] * 0.769 + rgb_array[i, j, 2] * 0.189)
                g = <int>(rgb_array[i, j, 0] * 0.349 +
                          rgb_array[i, j, 1] * 0.686 + rgb_array[i, j, 2] * 0.168)
                b = <int>(rgb_array[i, j, 0] * 0.272 +
                          rgb_array[i, j, 1] * 0.534 + rgb_array[i, j, 2] * 0.131)
                if r > 255:
                    r = 255
                if g > 255:
                    g = 255
                if b > 255:
                    b = 255

                new_array[j, i, 0], new_array[j, i, 1], new_array[j, i, 2], = r, g, b

    return pygame.image.frombuffer(new_array, (w, h), 'RGB')


cpdef sepia32_c(surface_):
    """
    Create a sepia image from the given Surface (compatible with 8, 24-32 bit with
    per-pixel information (image converted to convert_alpha())
    Surface converted to fast blit with pygame method convert() will raise a ValueError (Incompatible pixel format.).

    :param surface_:  Pygame.Surface converted with pygame method convert_alpha. Surface without per-pixel transparency
    will raise a ValueError (Incompatible pixel format.).
    :return: Returns a pygame.Surface (surface with per-pixel transparency)
    """

    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)

    cdef int w, h
    w, h = surface_.get_size()

    try:
        rgb_ = pixels3d(surface_)
        alpha_ = pixels_alpha(surface_)

    except (pygame.error, ValueError):
            # unsupported colormasks for alpha reference array
            raise ValueError('\nIncompatible pixel format.')
    cdef:
        unsigned char [:, :, :] rgb_array = rgb_
        unsigned char [:, :, :] new_array = empty((h, w, 4), dtype=uint8)
        unsigned char [:, :] alpha_array = alpha_
        int i=0, j=0
        int r, g, b
    with nogil:
        for i in prange(w):
            for j in range(h):
                r = <int>(rgb_array[i, j, 0] * 0.393 +
                          rgb_array[i, j, 1] * 0.769 + rgb_array[i, j, 2] * 0.189)
                g = <int>(rgb_array[i, j, 0] * 0.349 +
                          rgb_array[i, j, 1] * 0.686 + rgb_array[i, j, 2] * 0.168)
                b = <int>(rgb_array[i, j, 0] * 0.272 +
                          rgb_array[i, j, 1] * 0.534 + rgb_array[i, j, 2] * 0.131)

                if r > 255:
                   r = 255
                if g > 255:
                   g = 255
                if b > 255:
                   b = 255

                new_array[j, i, 0], new_array[j, i, 1], \
                new_array[j, i, 2], new_array[j, i, 3] = r, g, b, alpha_array[i, j]

    return pygame.image.frombuffer(new_array, (w, h), 'RGBA')


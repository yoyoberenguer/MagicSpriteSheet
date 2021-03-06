# cython: boundscheck=False, wraparound=False, nonecheck=False, cdivision=True, optimize.use_switch=True
# encoding: utf-8
import warnings

try:
    import pygame
    from pygame.surfarray import pixels3d, pixels_alpha
    from pygame import Surface
    from pygame.image import frombuffer

except ImportError:
    raise ImportError("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")

try:
    cimport cython
    from cython.parallel cimport prange
except ImportError:
    raise ImportError("\n<cython> library is missing on your system."
          "\nTry: \n   C:\\pip install cython on a window command prompt.")

try:
    import numpy
    from numpy import empty, uint8, zeros, float32
except ImportError:
    raise ImportError("\n<Numpy> library is missing on your system."
          "\nTry: \n   C:\\pip install numpy on a window command prompt.")

DEF ONE_255 = 1.0/255.0
DEF ONE_360 = 1.0/360.0


# EXTERNAL C CODE (file 'hsl_c.c')
cdef extern from 'hsl_c.c' nogil:
    struct hsl:
        double h
        double s
        double l

    struct rgb:
        double r
        double g
        double b

    struct rgba:
        double r
        double g
        double b
        double a

    hsl struct_rgb_to_hsl(double r, double g, double b)nogil;
    rgb struct_hsl_to_rgb(double h, double s, double l)nogil;

ctypedef hsl HSL
ctypedef rgb RGB


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


cpdef hsl_surface24c(surface_, double shift_):
    """
    HSL (HUE, SATURATION, LIGHTNESS) ROTATION OF PIXELS 
    
    * Video system must be initialised 
    * Return a 24-bit texture with HSL rotation. The image is converted to fast blit 
    * shift_ range [0.0 ... 1.0] equivalent to [0.0 ... 360.0] degrees
    
    :param surface_: pygame.Surface; Surface 24-bit without transparency layer  
    :param shift_  : shift range [0.0 ... 1.0] equivalent to [0.0 ... 360.0] degrees
    :return: Return a 24-bit texture with HSL rotation. The image is converted to fast blit 
    """

    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)
    assert isinstance(shift_, float), \
            'Expecting double for argument shift_, got %s ' % type(shift_)
    assert 0.0<= shift_ <=1.0, 'Positional argument shift_ should be between[0.0 .. 1.0]'

    cdef int width, height
    width, height = surface_.get_size()

    cdef:
        unsigned char [:, :, :] rgb_array

    try:
        rgb_array = pixels3d(surface_)

    except (pygame.error, ValueError):
        raise ValueError('\nInvalid pixel format.')

    cdef:
        unsigned char [:, :, ::1] new_array = zeros((height, width, 3), dtype=uint8)
        int i=0, j=0
        HSL hsl_
        RGB rgb_
        unsigned char r, g, b

    with nogil:
        for i in prange(width, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(height):
                r, g, b = rgb_array[i, j, 0], rgb_array[i, j, 1], rgb_array[i, j, 2]

                hsl_ = struct_rgb_to_hsl(r * ONE_255, g * ONE_255, b * ONE_255)
                hsl_.h = hsl_.h + shift_
                rgb_ = struct_hsl_to_rgb(hsl_.h, hsl_.s, hsl_.l)

                new_array[j, i, 0], new_array[j, i, 1], \
                new_array[j, i, 2] = <unsigned char>(rgb_.r*255.0), \
                                     <unsigned char>(rgb_.g*255.0), <unsigned char>(rgb_.b*255.0)

    return frombuffer(new_array, (width, height), 'RGB').convert()


cpdef void hsl_surface24c_inplace(surface_, double shift_):
    """
    HSL (HUE, SATURATION, LIGHTNESS) ROTATION OF PIXELS 
    
    * Video system must be initialised 
    * shift_ range [0.0 ... 1.0] equivalent to [0.0 ... 360.0] degrees
    
    :param surface_: pygame.Surface; Surface 24-bit without transparency layer  
    :param shift_  : shift range [0.0 ... 1.0] equivalent to [0.0 ... 360.0] degrees
    :return: void
    """

    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)
    assert isinstance(shift_, float), \
            'Expecting double for argument shift_, got %s ' % type(shift_)
    assert 0.0<= shift_ <=1.0, 'Positional argument shift_ should be between[0.0 .. 1.0]'

    cdef int width, height
    width, height = surface_.get_size()

    cdef:
        unsigned char [:, :, :] rgb_array

    try:
        rgb_array = pixels3d(surface_)

    except (pygame.error, ValueError):
        raise ValueError('\nInvalid pixel format.')

    cdef:
        int i=0, j=0
        HSL hsl_
        RGB rgb_
        unsigned char r, g, b

    with nogil:
        for i in prange(width, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(height):
                r, g, b = rgb_array[i, j, 0], rgb_array[i, j, 1], rgb_array[i, j, 2]

                hsl_ = struct_rgb_to_hsl(r * ONE_255, g * ONE_255, b * ONE_255)
                hsl_.h = hsl_.h + shift_
                rgb_ = struct_hsl_to_rgb(hsl_.h, hsl_.s, hsl_.l)

                rgb_array[i, j, 0], rgb_array[i, j, 1], \
                rgb_array[i, j, 2] = <unsigned char>(rgb_.r*255.0), \
                                     <unsigned char>(rgb_.g*255.0), <unsigned char>(rgb_.b*255.0)


cpdef hsl_surface32c(surface_, float shift_):
    """
    HSL (HUE, SATURATION, LIGHTNESS) ROTATION OF PIXELS 
    
    * Video system must be initialised 
    * Return a 32-bit texture with HSL rotation. The image is converted to fast blit 
    * shift_ range [0.0 ... 1.0] equivalent to [0.0 ... 360.0] degrees
    
    :param surface_: pygame.Surface; Surface 32-bit with transparency layer  
    :param shift_  : shift range [0.0 ... 1.0] equivalent to [0.0 ... 360.0] degrees
    :return: Return a 32-bit texture with HSL rotation. The image is converted to fast blit 
    """

    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)
    assert isinstance(shift_, float), \
           'Expecting float for argument shift_, got %s ' % type(shift_)
    assert 0.0 <= shift_ <= 1.0, 'Positional argument shift_ should be between[0.0 .. 1.0]'

    cdef:
        unsigned char [:, :, :] rgb_array
        unsigned char [:, :] alpha_array

    try:
        rgb_array = pixels3d(surface_)
        alpha_array = pixels_alpha(surface_)

    except (pygame.error, ValueError):
       raise ValueError('Compatible only for 32-bit format with per-pixel transparency.')

    cdef int width, height
    width, height = surface_.get_size()

    cdef:
        unsigned char [:, :, ::1] new_array = empty((height, width, 4), dtype=uint8)
        int i=0, j=0
        unsigned char r, g, b
        HSL hsl_
        RGB rgb_

    with nogil:
        for i in prange(width, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(height):
                r, g, b = rgb_array[i, j, 0], rgb_array[i, j, 1], rgb_array[i, j, 2]
                hsl_ = struct_rgb_to_hsl(r * ONE_255, g * ONE_255, b * ONE_255)
                hsl_.h = hsl_.h + shift_
                rgb_ = struct_hsl_to_rgb(hsl_.h, hsl_.s, hsl_.l)

                new_array[j, i, 0], new_array[j, i, 1], \
                new_array[j, i, 2], new_array[j, i, 3] = \
                    <unsigned char> (rgb_.r * 255.0), <unsigned char> (rgb_.g * 255.0), \
                    <unsigned char>(rgb_.b * 255.0), alpha_array[i, j]

    return frombuffer(new_array, (width, height ), 'RGBA').convert_alpha()



cpdef void hsl_surface32c_inplace(surface_, float shift_):
    """
    HSL (HUE, SATURATION, VALUE) ROTATION OF PIXELS 

    * Video system must be initialised 
    * Return a 32-bit texture with HSL rotation. The image is converted to fast blit 
    * shift_ range [0.0 ... 1.0] equivalent to [0.0 ... 360.0] degrees

    :param surface_: pygame.Surface; Surface 32-bit with transparency layer  
    :param shift_  : shift range [0.0 ... 1.0] equivalent to [0.0 ... 360.0] degrees
    :return: Return a 32-bit texture with HSL rotation. The image is converted to fast blit (convert_alpha)
    """

    assert isinstance(surface_, Surface), \
           'Expecting Surface for argument surface_ got %s ' % type(surface_)
    assert isinstance(shift_, float), \
           'Expecting float for argument shift_, got %s ' % type(shift_)
    assert 0.0 <= shift_ <= 1.0, 'Positional argument shift_ should be between[0.0 .. 1.0]'


    cdef:
            unsigned char [:, :, :] rgb_array
            unsigned char [:, :] alpha_array

    try:
        rgb_array = pixels3d(surface_)
        alpha_array = pixels_alpha(surface_)
    except (pygame.error, ValueError):
       raise ValueError('Compatible only for 32-bit format with per-pixel transparency.')

    cdef int width, height
    width, height = surface_.get_size()

    cdef:
        int i=0, j=0
        double r, g, b
        HSL hsl_
        RGB rgb_

    with nogil:
        for i in prange(width, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(height):
                r, g, b = rgb_array[i, j, 0], rgb_array[i, j, 1], rgb_array[i, j, 2]
                hsl_ = struct_rgb_to_hsl(r * ONE_255, g * ONE_255, b * ONE_255)
                hsl_.h = hsl_.h + shift_
                rgb_ = struct_hsl_to_rgb(hsl_.h, hsl_.s, hsl_.l)

                rgb_array[i, j, 0], rgb_array[i, j, 1], \
                rgb_array[i, j, 2], rgb_array[i, j, 3] = \
                    <unsigned char> (rgb_.r * 255.0), <unsigned char> (rgb_.g * 255.0), \
                    <unsigned char>(rgb_.b * 255.0), alpha_array[i, j]



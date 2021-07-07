import pygame
from SpriteTools import transition, blend_to_textures_inplace_24c, blend_to_textures_24c, color_reduction24_c, \
    dithering24_c, \
    bilateral_filter24_c, median_filter24_c, sobel24, greyscale_lightness32_c, greyscale_lightness24_c, Sobel4, sobel32, \
    median_filter32_c, color_reduction32_c, pixelate24, create_pixel_blocks_rgba, pixelate32
from GaussianBlur5x5 import blur5x5_surface24_inplace_c, canny_blur5x5_surface24_c, canny_blur5x5_surface32_c


#
# screen = pygame.display.set_mode((512, 512))
# # im1 = pygame.image.load("Assets\\Graphics\\Background\\test_remove\\A1.png").convert()
# im2 = pygame.image.load("Assets\\Graphics\\Background\\test_remove\\A4.png").convert()
# im2 = pygame.transform.smoothscale(im2, (512, 512))
#
# image1 = pygame.surfarray.make_surface(canny_blur5x5_surface24_c(im2))
# image1 = greyscale_lightness24_c(image1)
# image1 = pygame.surfarray.make_surface(sobel24(image1, 20))
# image2 = median_filter24_c(im2, 4)
# image2.blit(image1, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
# image2 = color_reduction24_c(image2, 16)
#
# #
# # # im1 = pygame.transform.smoothscale(im1, (512, 256))
# # im2 = pygame.transform.smoothscale(im2, (512, 512))
# # # blur5x5_surface24_inplace_c(im2)
# # im3 = greyscale_lightness_c(im2)
# # image = pygame.surfarray.make_surface(sobel(im3, 128))
# # image1 = median_filter24_c(im2, 4)
# # image1.blit(image, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
# # #image1 = median_filter24_c(image1, 8)
#
# i = 0
# while 1:
#     screen.fill((0, 0, 0, 0))
#     pygame.event.pump()
#     screen.blit(image2, (0, 0))
#     pygame.display.flip()
#     pygame.time.delay(16)
#     i += 0.1
#     if i > 100:
#         i = 100
#     print(i)

#
# screen = pygame.display.set_mode((512, 512))
#
# im2 = pygame.image.load("Assets\\Graphics\\MagicSpriteSheet\\EPIMET_256x256.png").convert_alpha()
# im2 = pygame.transform.smoothscale(im2, (512, 512))
#
# image1 = canny_blur5x5_surface32_c(im2)
# image1 = greyscale_lightness32_c(image1)
# image1 = sobel32(image1, 20)
# image2 = median_filter32_c(im2, 4)
# image2.blit(image1, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
# image2 = color_reduction32_c(image2, 16)
#
#
# i = 0
# while 1:
#     screen.fill((100, 0, 0, 0))
#     pygame.event.pump()
#     screen.blit(image2, (0, 0))
#     pygame.display.flip()
#     pygame.time.delay(16)
#     i += 0.1
#     if i > 100:
#         i = 100
#     print(i)



screen = pygame.display.set_mode((512, 512))

im2 = pygame.image.load("Assets\\python logo.png").convert_alpha()
im2 = pygame.transform.smoothscale(im2, (512, 512))

subs = create_pixel_blocks_rgba(im2, 16, 32, 32)

i = 0
for surface in subs:
    # avg=pygame.transform.average_color(surface)
    # surface.fill(avg)
    subs[i] = pixelate32(surface)
    i += 1
    ...

new_surface = pygame.Surface((512, 512))
new_surface.fill((0, 0, 0))

i=0
j=0
print(len(subs))
for pixel_block in subs:

    new_surface.blit(pixel_block, (i, j))
    i += 16
    if i >= 512:
        j += 16
        i = 0



i = 0
j = 0
while 1:
    pygame.event.pump()
    screen.fill((100, 100, 100, 0))
    screen.blit(new_surface, (0, 0))

    pygame.display.flip()
    pygame.time.delay(16)


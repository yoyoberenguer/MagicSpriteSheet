# SpriteSheet Studio 
## Load a spritesheet and add special effects

### Version 1 contains the following effects 
All effects can be summed together, but some effect will cancel or diminish others such as 
greyscale effect or pixalated effect.

```
1 - blending effect (blend the sprite with a specific color and choose the intensity) 
2 - HSV (hue rotation), rotate the colors of your sprites. This 
    effect is great to create colorfull animation with different 
    color variation from the same model.
3 - Bloom, create a bloom effect using a selective bright pass filter, this 
    effect will increase the intensity of you explosion sprites
4 - Create saturarion effect
5 - Create a superb cartoon effect for all your sprites. This effect can 
    also create an edge detection effect (when both median filter and color
    reduction values are set to zero. 
6 - Create a Gaussian blur effect (kernel 5x5) of intensity x1 x2 x4 x6
    Blur your sprites to the desire intensity, or use the progressive flag
    to adjust the blur with the timeline.
7 - Glowing effect (load a specific image and chosse a glowing direction)
8 - RGB channels (select a model of your choice e.g BGR, GRB etc). Swap channels
    at your convenience or enable/ disable the channel of your choice.
9 - RGB split (apply to 24 bit image format only). Create an RGB split effect, 
    superpose effet of red, green and blue channels (choose the coorect offset to 
    move the channels at the suitable position)
10 - Transition effect, display your sprites and change the apperance toward a 
     specific texture (this is similar to a morphing effect) 
11 - Glitch effect (vertical and horizontal directions). Add a special motion to 
     your sprites to simulate a glitch effect that could enhence the animation
12 - Dithering effect, aesthetic effect to create a retro type animation 
13 - Pixalated effect, modify your sprites with pixalation effect with adjustable 
     pixels block's size.
14 - convert your sprite in sepia. Change the tone of your animation toward a smooth 
     sepia effect
15 - Greyscale effect. All will be sadly gray !
16 - Inverse effect, Inverse the sprites color

```

### Requirements:
```
Python > 3.0
future~=0.16.0
pygame~=2.0.1
numpy~=1.18.5
Pmw~=2.0.1
Pillow~=8.0.1
Cython~=0.29.21
```

### Installation
```
Download the executable file and run the installer (check the github release section)
New release v1.0.0-alpha
Actual version is a pre-release and the current project is stil under development and testing
Please report any issues if you wish them to be fixed.
```

![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Capture.PNG)

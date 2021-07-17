# SpriteSheet Studio 
## Load a spritesheet and add special effects

### Version 1 contains the following effects 
All effects can be summed together, but some effect will cancel or diminish others such as 
greyscale effect or pixalated effect.


* blending effect (blend the sprite with a specific color and choose the intensity) 
* HSV (hue rotation), rotate the colors of your sprites. This effect is great to create 
  colorful animation with different color variation from the same model.
* Bloom, create a bloom effect using a selective bright pass filter, this 
    effect will increase the intensity of you explosion sprites
* Create saturarion effect
* Create a superb cartoon effect for all your sprites. This effect can 
    also create an edge detection effect (when both median filter and color
    reduction values are set to zero. 
* Create a Gaussian blur effect (kernel 5x5) of intensity x1 x2 x4 x6
    Blur your sprites to the desire intensity, or use the progressive flag
    to adjust the blur with the timeline.
* Glowing effect (load a specific image and choose a glowing direction)
* RGB channels (select a model of your choice e.g BGR, GRB etc). Swap channels
    at your convenience or enable/ disable the channel of your choice.
* RGB split (apply to 24 bit image format only). Create an RGB split effect, 
    superpose effet of red, green and blue channels (choose the coorect offset to 
    move the channels at the suitable position)
* Transition effect, display your sprites and change the appearance toward a 
     specific texture (this is similar to a morphing effect) 
* Glitch effect (vertical and horizontal directions). Add a special motion to 
     your sprites to simulate a glitch effect that could enhence the animation
* Dithering effect, aesthetic effect to create a retro type animation 
* Pixalated effect, modify your sprites with pixalation effect with adjustable 
     pixels block's size.
* convert your sprite in sepia. Change the tone of your animation toward a smooth 
     sepia effect
* Greyscale effect. All will be sadly gray !
* Inverse effect, Inverse the sprites color



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

### Loading a spritesheet
```
Below a spritesheet that can be loaded by the interface. 
Observe the background color (solid black) and the number of sprites icnluded in the 
spritesheet. 
The image is composed by 8 columns and 8 rows and give us a total of 64 sprites 
To determine the sprite width and height we need to check first the spritesheet 
dimension (here 2048x2048 pixels), that give us the following sprite dimension, 
256x256 (2048 / 8) 

* The actual version (1.0.0 - alpha) does not include sprite padding functionaly nor  
  an automatic sprite size detection option (all the values have to be entered manually before 
  loading the spritesheet)
 
* It is also compulsory to know the image format (24-bit or 32-bit) and tick the correct option
  in the input settings. In our scenario, it will be a 24-bit image format (without per-pixel
  transparency)

```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/Miniature%20SpriteSheet%20example.png)
```
In order to load the above spritesheet we will enter the following values, tick the box 24-bit 
and load the file (the file must be JPG, PNG, GIF (non-animated),  BMP,  PCX, TGA (uncompressed)
TIF).

* If the image has a transparency background, select the 32-bit option instead
* The file will fail to load if the input values are not correct.
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/InputSettings.PNG)

### Blending effect
```
Blend the sprite with a specific color (ajust the blending percentage to obtain 
the required color effect). 
Set the exlude color to avoid the background to be blended otherwise the background
will included in the blend process.
Adjust the percentage with the scale.
```

![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/Blending.PNG)
```
HSV (for hue, saturation, value; also known as HSB, for hue, saturation,
brightness) are alternative representations of the RGB color model
This effect will change the color of your sprites to a define color or will rotate
the hue automatically for your animation starting a -180 degrees ending at 
+180 degres when the hsv rotate option is enabled.
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/HSV.PNG)
```
Bloom effect 
Bloom is a computer graphics effect used in video games, demos, and high dynamic range
rendering to reproduce an imaging artifact of real-world cameras.
The algorithm is based on my previous project bloom (have a look to my github page
to have a full understanding on how to)
The bloom effect will increase the brightness of your sprite creating a kind 
of bright halo of light aroud the object (sprite). 
It relies on a bright pass filter in order to find the brighest area in your 
image and enhance those areas. 
In the future version I will include an RGB color selections for the bloom effect
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/Bloom.PNG)
```
Saturation
Saturation refers to the intensity of a color. The higher the saturation of a 
color, the more vivid it is. The lower the saturation of a color, the closer 
it is to gray. Lowering the saturation of a photo can have a “muting” or calming 
effect, while increasing it can increase the feel of the vividness of the scene.
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/Saturation.PNG)
```
Cartoon effect
This is a appealing ffect that will modify your sprites into a cartonish model.
It is based on an edge detection algorithm (canny edge detection in addition 
with a median filter and color reduction). 
When the median filter & color reduction are null the sprites animation will be 
converted to an edge detection animation.
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/Cartoonish.PNG)
```
Blur Effect 
Apply a Gaussian blur effect kernel 5x5. 
Select the number of passes x2 x4 x6
The pixels outside the image are substitute for the adjacent edge pixel for example 
pixel [-2, 0] will be equivalent to pixel [0,0]
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/Blur.PNG)
```
GLOW effect 
Select a texture that will represent the glow motion an select a diretion 
note that the selected texture must match the direction otherwise the effect
will look odd. for example if you select the directions right and left the texture
would have to be a vertical shape (height > width). For up or down glowing effect 
the texture would have to be the opposite (width > height) 
In the main direction under Assets you can find texture that can be used for 
the glowing effect, such as icon_glareFx_blue, icon_glareFx_blue_top_left2bottom_right,
icon_glareFx_blue_top_right2bottom_left, icon_glareFx_red.
With the scale you can define a specific color for the glow effect.
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/Glow.PNG)
```
RGB channels 
Convert your sprites to a different model 
choose from the drop down menu any of this models 
RBG, RBG, GRB, BRG, BGR, GBR and activate or disable the color channel of your 
choice 
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/RGB%20channel.PNG)
```
RGB split effect
An RGB Split Effect results in photos that have a glitch-like appearance, where 
the colors that comprise all white light (red, green, blue) went out-of-bounds
select the x & y offset for the channels RGB. 
Specify the start and End value of the effect 
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/RGB%20split.PNG)
```
Transition 
This effect allows the sprites to merge toward a static texture. 
For example if you have a sprite animation of a errupting volcano effect, the transition
will smoothly merge to a final image that could be a cold volcano. 
Without any texture, the sprite animation will morph toward the background color
Texture must be a PNG, JPEG, BMP
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/Transition.PNG)
```
GLITCH 
Add a glitch effect to you sprites using a lateral / vertical motion
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/Glitch.PNG)
```
Dithering 
A common use of dither is converting a grayscale image to black and white, such 
that the density of black dots in the new image approximates the average gray-level
in the original.
select a value for the intensity effect maximun dithering effect is value equal zero 
```
```
Pixelated 
Create a pixelated effect for your sprites, choose the pixel block size as 
a multiple of 2 such as for example 4, 8, 16, 32, 64
```
```
Sepia 
Sepia is a reddish-brown color, named after the rich brown pigment derived from the 
ink sac of the common cuttlefish Sepia.
```
```
Greyscale 
In digital photography, computer-generated imagery, and colourimetry, a greyscale
image is one in which the value of each pixel is a single sample representing only
an amount of light; that is, it carries only intensity information. Greyscale 
images, a kind of black-and-white or grey monochrome, are composed exclusively 
of shades of grey. The contrast ranges from black at the weakest intensity to white
at the strongest
```
![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/Assets/Miscellaneous.PNG)


## License (MIT)

Copyright (c) 2021 Yoann Berenguer

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

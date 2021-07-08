# SpriteSheet Studio 
## Load a spritesheet and add special effects

### Version 1 contains the following effects 
All effects can be summed together, but some effect will cancel or diminish others such as 
greyscale effect or pixalated effect.


* blending effect (blend the sprite with a specific color and choose the intensity) 
* HSV (hue rotation), rotate the colors of your sprites. This effect is great to create 
  colorfull animation with different color variation from the same model.
* Bloom, create a bloom effect using a selective bright pass filter, this 
    effect will increase the intensity of you explosion sprites
* Create saturarion effect
* Create a superb cartoon effect for all your sprites. This effect can 
    also create an edge detection effect (when both median filter and color
    reduction values are set to zero. 
* Create a Gaussian blur effect (kernel 5x5) of intensity x1 x2 x4 x6
    Blur your sprites to the desire intensity, or use the progressive flag
    to adjust the blur with the timeline.
* Glowing effect (load a specific image and chosse a glowing direction)
* RGB channels (select a model of your choice e.g BGR, GRB etc). Swap channels
    at your convenience or enable/ disable the channel of your choice.
* RGB split (apply to 24 bit image format only). Create an RGB split effect, 
    superpose effet of red, green and blue channels (choose the coorect offset to 
    move the channels at the suitable position)
* Transition effect, display your sprites and change the apperance toward a 
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

### Loading a sprite

![alt text](https://github.com/yoyoberenguer/MagicSpriteSheet/blob/main/InputSettings.png)


## License (MIT)

Copyright (c) 2021 Yoann Berenguer

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

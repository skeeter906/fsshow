#!/usr/bin/python
"""
fsshow -- A simple slideshow generator for Flickr hosted images.
Copyright (C) 2006 Mat Malone

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import shutil
from PIL import Image
from PIL import JpegImagePlugin
Image._initialized=2


class FitImage(object):
    def __init__(self, imagePath):
        self._imagePath = imagePath
        self._im = Image.open(imagePath)
    
    def Resize(self, xy, outPath):
        im = self._im.resize(xy, Image.ANTIALIAS)
        im.save(outPath)
        return outPath
    
    def DownsizeFit(self, xy, outPath):
        x,y = xy
        imX,imY = self._im.size
        
        if x >= imX and y >= imY:
            shutil.copyfile(self._imagePath, outPath)
            return outPath

        xCoeff = float(x)/float(imX)
        yCoeff = float(y)/float(imY)
        
        coeff = min(xCoeff, yCoeff)
        
        newX = int(imX*coeff)
        newY = int(imY*coeff)
        
        return self.Resize((newX,newY), outPath)

def GetCenterFromTopLeft(canvasXY, imageXY):
    canvasX,canvasY = canvasXY
    imageX,imageY = imageXY
    
    x = int(round((canvasX - imageX) / 2))
    y = int(round((canvasY - imageY) / 2))
    
    return (x,y)

if __name__ == "__main__":
    import os
    fitted = FitImage(os.path.join("cache" , "0.jpg"))
    print fitted.DownsizeFit((800,600), "imagingtest.jpg")
    print GetCenterFromTopLeft((800,600), (790, 592))
    

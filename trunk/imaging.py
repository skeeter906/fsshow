#!/usr/bin/python

# fsshow -- A simple slideshow generator for Flickr hosted images.
# Copyright (C) 2006 Mat Malone
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from PIL import Image
import shutil

class FitImage(object):
    def __init__(self, imagePath):
        self._imagePath = imagePath
        self._im = Image.open(imagePath)
    
    def Resize(self, xy):
        im = self._im.resize(xy, Image.ANTIALIAS)
        newPath = "fitted_" + self._imagePath
        im.save(newPath)
        return newPath
    
    def DownsizeFit(self, xy):
        x,y = xy
        imX,imY = self._im.size
        
        if x >= imX and y >= imY:
            shutil.copyfile(self._imagePath, "fitted_" + self._imagePath)
            return "fitted_" + self._imagePath

        xCoeff = float(x)/float(imX)
        yCoeff = float(y)/float(imY)
        
        coeff = min(xCoeff, yCoeff)
        
        newX = int(imX*coeff)
        newY = int(imY*coeff)
        
        return self.Resize((newX,newY))

if __name__ == "__main__":
    fitted = FitImage("1.jpg")
    print fitted.DownsizeFit((800,600))
    
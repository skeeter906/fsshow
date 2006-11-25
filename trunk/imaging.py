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

class FitImage(object):
    def __init__(self, imagePath):
        self._imagePath = imagePath
        self._im = Image.open(imagePath)
    
    def Resize(self, xy):
        im = self._im.resize(xy, Image.ANTIALIAS)
        newPath = "fitted_" + self._imagePath
        im.save(newPath)
        return newPath

if __name__ == "__main__":
    fitted = FitImage("0.jpg")
    print fitted.Resize((800,600))
    
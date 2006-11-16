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

import flickr

class SlideshowModel(object):
    """
    This class handles data modeling for the fsshow program. Photo sets and
    images are acquired through this interface.
    """
    def __init__(self):
        self.slides = []
        self.searchParams = {}
        self.currentIndex = 0

    def SearchParam(self, key, value):
        """
        Define a tuple key/value pair which acts as a search paramater. Call
        of this method adds a parameter with a logical AND.
        """
        self.searchParams[key] = value
        
    def Find(self):
        """
        Processes the entered search parameters.
        """
        self.factory = FlickrSlideFactory()
        
        newSlides = self.factory.Build(self.searchParams)
        
        self.slides.extend(newSlides)
        
        return self.slides
    

class SlideFactory(object):
    """
    Abstract factory base class for slides.
    """
    def __init__(self):
        self.photos = []
    
    def Build(self, searchParams):
        self.searchParams = searchParams
        self.BuildProcess()
        
        return self.photos

class FlickrSlideFactory(SlideFactory):
    """
    Concrete implementation of SlideFactory for Flickr.
    """
    def __init__(self):
        super(FlickrSlideFactory, self).__init__()
    
    def BuildProcess(self):
        me = flickr.people_findByEmail("m2@innerlogic.org")
        if "email" in self.searchParams: self.__ProcessEmail()


    def __ProcessEmail(self):
        print "processing email"
        user = flickr.people_findByEmail("m2@innerlogic.org")
        self.__ProcessEmailPages(user)
        
    def __ProcessEmailPages(self, user):
        for photo in flickr.favorites_getPublicList(user.id, 50, 0):
            self.photos.append(FlickrSlide(photo))

    
class Slide(object):
    """
    A single photo in the slideshow.
    """
    def __init__(self, photo):
        self.photo = photo
        
    def GetTitle(self): pass
    def GetUrl(self): pass
    
class FlickrSlide(Slide):
    """
    Concrete implementation of a Slide on Flickr
    """
    def GetTitle(self):
        """
        Returns the title of the slide.
        """
        u = unicode(self.photo.title)
        return u.encode("utf8", "replace")
    def GetUrl(self):
        """
        Returns the URL of the image.
        """
        return self.photo.GetURL()

    
if __name__ == "__main__":
    model = SlideshowModel()
    model.SearchParam("email", "m2@innerlogic.org")
    for slide in model.Find(): print slide.GetTitle()

    
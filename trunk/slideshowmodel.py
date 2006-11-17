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

import flickr, util, urllib, os, time, threading

class SlideshowModel(object):
    """
    This class handles data modeling for the fsshow program. Photo sets and
    images are acquired through this interface.
    """
    def __init__(self):
        self.slides = []
        self._searchParams = {}
        self._currentIndex = 0

    def SearchParam(self, key, value):
        """
        Define a tuple key/value pair which acts as a search paramater. Call
        of this method adds a parameter with a logical AND.
        """
        self._searchParams[key] = value
        
    def Find(self):
        """
        Processes the entered search parameters.
        """
        self.factory = FlickrSlideFactory()
        
        newSlides = self.factory.Build(self._searchParams)
        
        self.slides.extend(newSlides)

    def FetchSlide(self):
        if self._currentIndex >= len(self.slides): return None
        
        slide = self.slides[self._currentIndex]
        self._currentIndex += 1
        return slide
    
    def FetchImage(self):
        slide = self.FetchSlide()
        
        if not slide: raise Exception("No more slides")
        
        slide.GetImage(str(self._currentIndex) + ".jpg")
        
        path = slide.GetLocalPath()
        
        print "path = ", path
    
    def Go(self):
        THREAD_LIMIT = 5
        while True:
            # limit number of threads
            while threading.activeCount() > THREAD_LIMIT:
                time.sleep(1)
            
            util.debugLog("creating new thread")
            t = threading.Thread(target=self.FetchImage)
            id = t.getName()
            util.debugLog("threadid: " + str(id))
            t.start()


            #path = self.FetchImage()
            
            #if not path: break
            
            #print "path = ", path
        
        return True

class SlideFactory(object):
    """
    Abstract factory base class for slides.
    """
    def __init__(self):
        self.photos = []
    
    def Build(self, searchParams):
        self._searchParams = searchParams
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
        if "email" in self._searchParams: self.__ProcessEmail()


    def __ProcessEmail(self):
        print "processing email"
        user = flickr.people_findByEmail("m2@innerlogic.org")
        self.__ProcessEmailPages(user)
        
    def __ProcessEmailPages(self, user):
        PER_PAGE = 50
        page = 0

        while True:
            photos = flickr.favorites_getPublicList(user.id, PER_PAGE, page)
            slides = [FlickrSlide(slide) for slide in photos]
            self.photos.extend(slides)
            if len(photos) < PER_PAGE: break
            if len(self.photos) > PER_PAGE * 2: break


    
class Slide(object):
    """
    A single photo in the slideshow.
    """
    def __init__(self, photo):
        self._photo = photo
        
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
        u = unicode(self._photo.title)
        return u.encode("utf8", "replace")
    
    def GetUrl(self):
        """
        Returns the URL (string) of the image.
        """
        try:
            url = self._photo.getURL(size='Original', urlType='source')
        except flickr.FlickrError:
            util.debugLog("Original size not found")
            try:
                url = self._photo.getURL(size='Large', urlType='source')
            except flickr.FlickrError:
                util.debugLog("Large size not found")
                url = self._photo.getURL(size='Medium', urlType='source')
        
        self._url = url
        return url
    
    def GetImage(self, outPath):
        """
        Downloads the image file to the specified path.
        
        Returns True on success.
        """
        self._localPath = outPath
        
        # get the URL if it's not already saved
        if not hasattr(self, "_url"): self.GetUrl()
        
        data = urllib.urlopen(self._url).read()
        
        try:
            fd = open(outPath, "wb")
            fd.write(data)
        finally:
            fd.close()
        
        util.debugLog("Saved " + self._url + " to " + outPath)
        
        return True
    
    def GetLocalPath(self):
        return self._localPath
    
    
if __name__ == "__main__":
    model = SlideshowModel()
    model.SearchParam("email", "m2@innerlogic.org")
    model.Find()
    
    count = 0
    #while True:
    #    path = model.FetchImage()
    #    
    #    print "fetched path: ", path
    #    
    #    count += 1
    model.Go()
    print "done printing"

    
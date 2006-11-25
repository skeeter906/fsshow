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
        # Thread-insentive members
        self._slides = []
        self._searchParams = {}
        self._currentIndex = 0
        
        # Thread-sensitive members
        self._imagePaths = []
        self._lock = threading.Lock()
        self._workerCounter = util.ThreadCounter()        

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
        
        self._slides.extend(newSlides)
        
        util.debugLog("Find(): retrieved " + str(len(self._slides)) + " slides")

    def FetchSlide(self):
        if self._currentIndex >= len(self._slides): return None
        
        slide = self._slides[self._currentIndex]
        self._currentIndex += 1
        return slide
    
    def FetchImage(self, slide, outPath):
        """
        Retrieves an image from Flickr and stores it in the model.
        """
        slide.GetImage(outPath)
        
        path = slide.GetLocalPath()
        
        self._lock.acquire()
        util.debugLog(outPath + " acquired lock",2)
        self._imagePaths.append(path)
        util.debugLog(outPath + " releasing lock",2)
        self._lock.release()
        self._workerCounter.Down()
    
    def NextImagePath(self):
        """
        Get the path of next slide in the show.
        """
        path = True
        
        self._lock.acquire()
        util.debugLog("NextImagePath acquired lock", 2)
        if self._currentIndex >= len(self._slides):
            util.debugLog("out of slides")
            path = None
            
        if not self._currentIndex >= len(self._imagePaths):        
            path = self._imagePaths[self._currentIndex]
            self._currentIndex += 1
            
        util.debugLog("NextImagePath releasing lock", 2)
        self._lock.release()
        
        return path

    def Start(self):
        """
        Kicks off the fetching of slide images. Continues to run until worker
        threads have finished.
        """
        THREAD_LIMIT = 5
        
        for k,slide in enumerate(self._slides):
            # limit number of threads
            while self._workerCounter.Get() >= THREAD_LIMIT:
                time.sleep(1)
            
            util.debugLog("creating new thread")
            t = threading.Thread(target=self.FetchImage,
                                 kwargs={"slide":slide, "outPath":str(k) + ".jpg"})
            id = t.getName()
            
            util.debugLog("threadid: " + str(id),2)
            
            # increment the thread counter before we start
            self._workerCounter.Up()
            
            t.start()
        
        while not self._workerCounter.WasTouched() or self._workerCounter.Get() > 0:
            util.debugLog("waiting for threads " + str(self._workerCounter.Get())
                          + " to finish")
            time.sleep(1)
        
        util.debugLog("All threads have completed")
        
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
        util.debugLog("processing email")
        user = flickr.people_findByEmail("m2@innerlogic.org")
        self.__ProcessEmailPages(user)
        
    def __ProcessEmailPages(self, user):
        PER_PAGE = 5
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
        util.debugLog(self._localPath + " fetching URL",2)
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
        
        util.debugLog(self._localPath + " downloading image",2)
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

class SlideshowModelException(Exception): pass
class SlideshowModelDone(SlideshowModelException): pass

if __name__ == "__main__":
    count = 0
    model = SlideshowModel()
    model.SearchParam("email", "m2@innerlogic.org")
    model.Find()
    
    #model.Start()
    t = threading.Thread(target=model.Start)
    t.start()

    while True:
        path = model.NextImagePath()
        if path is True:
            time.sleep(1)
            continue
        elif path == None:
            break
        print str(count), ": ", path
        count += 1
    print "slideshow finished"
    
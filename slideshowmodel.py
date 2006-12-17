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

import flickr
import util
import urllib
import os
import time
import threading

class SlideshowModel(object):
    """
    This class handles data modeling for the fsshow program. Photo sets and
    images are acquired through this interface.
    """
    def __init__(self):
        # Thread-insentive members
        self._searchParams = {}
        self._isRunning = False
        self._shortWaitSecs = .5

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
        # init some of the searching things
        self._PreStart()
        self._slides = []
        self.factory = FlickrSlideFactory()
        newSlides = self.factory.Build(self._searchParams)
        self._slides.extend(newSlides)
        util.debugLog("Find(): retrieved " + str(len(self._slides)) + " slides")
        # reset search params
        self._searchParams = {}
        
    def FetchImage(self, slide, outPath):
        """
        Retrieves an image from Flickr and stores it in the model.
        """
        slide.GetImage(outPath)
        self._lock.acquire()
        util.debugLog(outPath + " acquired lock",2)
        # make sure the model wasn't Stop()'d
        if not self._continue:
            return self._ShutdownWorker(slide, outPath)
        self._readySlides.append(slide)
        util.debugLog(outPath + " releasing lock",2)
        self._lock.release()
        self._workerCounter.Down()    

    def CurrentImagePath(self):
        """
        Returns the path of the current slide in the show.
        """
        return self._readySlides[self._currentIndex].GetLocalPath()

    def CurrentTitle(self):
        """
        Returns the title of the current slide in the show.
        """
        if hasattr(self, "_currentIndex"):
            return self._readySlides[self._currentIndex].GetTitle()
        return None
    
    def CurrentAuthor(self):
        """
        Returns the title of the current slide in the show.
        """
        if hasattr(self, "_currentIndex"):
            return self._readySlides[self._currentIndex].GetAuthor()
        return None
    
    def AddIndex(self, n):
        """
        Adds n to the current slide index. May be positive or
        negative.
        Returns True on success; None if there is a slide(s) left by
        it is still downloading; False if there are no more slides in
        the queue.
        """
        self._lock.acquire()
        util.debugLog("AddIndex() acquired lock", 2)
        if self._currentIndex+n >= len(self._slides) or self._currentIndex+n < 0:
            # out of slides
            util.debugLog("out of slides")
            status = False  
        elif self._currentIndex+n >= len(self._readySlides):
            # wait for more to download
            util.debugLog("wait for more slides to download",2)
            status = None
        else:
            # found a slide
            util.debugLog("found a slide",2)
            status = True
            self._currentIndex += n
        util.debugLog("AddIndex() releasing lock", 2)
        self._lock.release()
        return status
        
    def Next(self):
        """
        Moves the current index to the next slide.
        Returns True on success; None if there is a slide(s) left by
        it is still downloading; False if there are no more slides in
        the queue.
        """
        return self.AddIndex(1)
    
    def Previous(self):
        """
        Moves the current index to the previous slide.
        Returns True on success; None if there is a slide(s) left by
        it is still downloading; False if there are no more slides in
        the queue.
        """        
        return self.AddIndex(-1)
        
    def Start(self):
        """
        Kicks off the fetching of slide images. Continues to run until worker
        threads have finished.
        """
        THREAD_LIMIT = 5
        self._isRunning = True
        for k,slide in enumerate(self._slides):
            # check to see if Stop() was called
            if not self._continue: break
            # limit number of threads
            while self._workerCounter.Get() >= THREAD_LIMIT:
                time.sleep(self._shortWaitSecs)
            util.debugLog("creating new thread")
            t = threading.Thread(target=self.FetchImage,
                                 kwargs={"slide":slide, "outPath":os.path.join("cache", str(k) + ".jpg")})
            id = t.getName()
            util.debugLog("threadid: " + str(id),2)
            # increment the thread counter before we start
            self._workerCounter.Up()
            t.start()
        
        while not self._workerCounter.WasTouched() or self._workerCounter.Get() > 0:
            util.debugLog("waiting for threads " + str(self._workerCounter.Get())
                          + " to finish")
            time.sleep(self._shortWaitSecs)
        self._isRunning = False
        util.debugLog("All threads have completed")
        return True

    def _ShutdownWorker(self, slide, outPath):
        util.debugLog(outPath + " releasing lock",2)
        self._lock.release()
        os.unlink(slide.GetLocalPath())
        self._workerCounter.Down()        

    def _PreStart(self):
        """
        Sets up some status and synchronization members at the start
        of each show.
        """
        while self.IsRunning():
            # wait for previous slideshows to finish
            self.Stop()
            util.debugLog("waiting for "
                          + str(self._workerCounter.Get())
                          + " threads to finish before PreStart")
            time.sleep(self._shortWaitSecs)
        self._continue = True
        self._currentIndex = 0
        self._readySlides = []
        # Thread-sensitive members
        self._lock = threading.Lock()
        self._workerCounter = util.ThreadCounter()
    
    def Stop(self):
        self._continue = False
    
    def Cleanup(self):
        # cleanup tmp files
        if hasattr(self, "_readySlides"):
            for slide in self._readySlides:
                util.debugLog("Cleanup: deleting " + slide.GetLocalPath(), 2)
                try:
                    os.unlink(slide.GetLocalPath())
                except IOError: pass
    
    def IsRunning(self):
        """
        Returns true if the Start() loop is currently running.
        """
        return self._isRunning
    
class SlideFactory(object):
    """
    Abstract factory base class for slides.
    """
    def __init__(self):
        self.photos = []
    
    def Build(self, searchParams):
        """
        Processes the search parameters and returns the list of photos.
        """
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
        if "email" in self._searchParams: self._ProcessEmail()
        elif "url" in self._searchParams: self._ProcessUrl()
        elif "username" in self._searchParams: self._ProcessUsername()
        
    def _ProcessUrl(self):
        util.debugLog("processing url " + self._searchParams["url"])
        user = flickr.people_findByURL(self._searchParams["url"])
        self._ProcessUserPages(user)        
        
    def _ProcessEmail(self):
        util.debugLog("processing email " + self._searchParams["email"])
        user = flickr.people_findByEmail(self._searchParams["email"])
        self._ProcessUserPages(user)
        
    def _ProcessUsername(self):
        util.debugLog("processing username " + self._searchParams["username"])
        user = flickr.people_findByUsername(self._searchParams["username"])
        self._ProcessUserPages(user)
        
    def _ProcessUserPages(self, user):
        PER_PAGE = 5
        page = 1
        while True:
            try:
                photos = flickr.favorites_getPublicList(user.id, PER_PAGE, page)
            except AttributeError:
                raise SlideshowModelNoSlides("No slides found")
            slides = [FlickrSlide(slide) for slide in photos]
            self.photos.extend(slides)
            if len(photos) < PER_PAGE: break
            if len(self.photos) > PER_PAGE * 2: break
            page += 1
    
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
    
    def GetAuthor(self):
        """
        Returns the author of the slide.
        """
        u = unicode(self._photo.owner.username)
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
        """
        Returns the path of the image on the local disk.
        """
        return self._localPath

class SlideshowModelException(Exception): pass
class SlideshowModelDone(SlideshowModelException): pass
class SlideshowModelNoSlides(SlideshowModelException): pass

if __name__ == "__main__":
    util.DEBUG_LEVEL = 10
    count = 0
    loopCount = 0
    model = SlideshowModel()
    model.SearchParam("email", "m2@innerlogic.org")
    #model.SearchParam("username", "test")
    model.Find()
    t = threading.Thread(target=model.Start)
    t.start()
    while True:
        if count > 0: status = model.Next()
        else: status = model.AddIndex(0)
        if status is None:
            time.sleep(1)
            continue
        elif status is False:
            break
        print count, ":", model.CurrentTitle(), ":", model.CurrentAuthor(), ":", model.CurrentImagePath()
        count += 1
    print "slideshow finished"
    model.Stop()
    model.Cleanup()
    print "done with Cleanup"
    

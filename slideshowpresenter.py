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

import util
import threading
import time
import slideshowmodel

class SlideshowPresenter(object):
    """
    Standard presenter class for the fsshow program. Is passed all the other
    main objects in the system.
    """
    def __init__(self, model, view, interactor):
        self.model = model
        self.view = view
        self.interactor = interactor
        interactor.Install(self, view)
        self._isRunning = False
        self._shortWaitSecs = .5
        self._longWaitSecs = 5
        self._isListening = True
        #self._initView()
        view.Start()
        
    def _initView(self):
        """
        Sets up any defaults in the view object.
        """
        pass
        
    def StartSlideshow(self):
        """
        Starts the slideshow. Mostly sets up the model.
        """
        util.debugLog("SlideshowPresenter.StartSlideshow()")
        
        self._first = True
        try: 
            self._ModelSearch()
        except slideshowmodel.SlideshowModelNoSlides, inst:
            msg = str(inst)
            util.debugLog(msg)
            self.view.Popup(msg)
            return False
        self._ModelStart()
        self.StartTimer(self._shortWaitSecs)
    
    def _ModelSearch(self):
        self.view.UpdateStatus("Searching for photos...")
        self.model.SearchParam(util.getSearchParamType(self.interactor.searchString),
                               self.interactor.searchString)
        self.model.Find()
        
    def _ModelStart(self):
        self.view.UpdateStatus("Downloading photos...")
        t = threading.Thread(target=self.model.Start)
        t.start()
        self._isRunning = True
    
    def SetWaitSecs(self, waitSecs):
        """
        Configure the amount of seconds to wait between slides.
        """
        self._longWaitSecs = waitSecs
    
    def ShiftSlide(self, shift=1, blockTimer=False):
        """
        Moves or "shifts" a 'shift' number of slides in the queue.
        If blockTimer is true, then the timer is not set after calling.
        """
        # check see if we were even started
        if not self._isRunning: return False
        # don't go to the next picture if we've yet to show one
        if self._first is True: shift = 0
        status = self.model.AddIndex(shift)
        if status == None:
            util.debugLog("need to wait more for another slide",1)
            self.view.UpdateStatus("Waiting for next image to download...")
            # Init timer to call again in a bit
            if not blockTimer: self.StartTimer(self._shortWaitSecs)
        elif status == False:
            util.debugLog("no more slides")
            self.view.UpdateStatus("Slideshow finished")
        else:
            self.view.UpdateTitle(self.model.CurrentTitle())
            self.view.UpdateStatus("Drawing Image...")
            util.debugLog("showing current slide",2)
            path = self.model.CurrentImagePath()
            self._first = False
            self.view.ShowImage(path)
            if blockTimer: self.view.UpdateStatus("Ready")
            else: self.view.UpdateStatus("Playing slideshow...")
            # Init timer to call again in a while
            if not blockTimer: self.StartTimer(self._longWaitSecs)

    def CleanupSlideshow(self):
        """
        Stops the model, then clears the cache.
        """
        self.model.Stop()
        self.model.Cleanup()
        
    def StartTimer(self, waitSecs):
        """
        Initializes a Timer to show the next slide in the queue after a few
        seconds.
        """
        self.interactor.StartTimer(waitSecs)

    def StopTimer(self):
        """
        Stops the timer if it's running.
        """
        self.interactor.StopTimer()
        
if __name__ == "__main__":
    import slideshowmodel
    import slideshowview
    import slideshowinteractor    
    presenter = SlideshowPresenter(slideshowmodel.SlideshowModel(),
                                   slideshowview.SlideshowView(),
                                   slideshowinteractor.SlideshowInteractor())
    

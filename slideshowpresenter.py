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

import util
import threading
import time

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
        
        self._ModelSearch()
        self._ModelStart()
        self._SetTimer()
    
    def _ModelSearch(self):
        self.view.UpdateStatus("Searching for photos...")
        self.model.SearchParam("email", "m2@innerlogic.org")
        self.model.Find()
        
    def _ModelStart(self):
        self.view.UpdateStatus("Downloading photos...")
        t = threading.Thread(target=self.model.Start)
        t.start()
    
    def ShowNextSlide(self, blockTimer=False):
        path = self.model.NextImagePath()
        if path is True:
            util.debugLog("need to wait more for another slide",2)
        elif path == None:
            util.debugLog("no more slides")
            return
        else:
            self.view.ShowImage(path)
        
        # Init timer to call again in a bit
        if not blockTimer: self._SetTimer()
    
    def CleanupSlideshow(self):
        self.model.Stop()
        
    def _SetTimer(self, waitSecs=5):
        """
        Initializes a Timer to show the next slide in the queue after a few
        seconds.
        """
        #threading.Timer(waitSecs, self.ShowNextSlide).start()
        self.interactor.StartTimer(waitSecs)
        
if __name__ == "__main__":
    import slideshowmodel
    import slideshowview
    import slideshowinteractor    
    presenter = SlideshowPresenter(slideshowmodel.SlideshowModel(),
                                   slideshowview.SlideshowView(),
                                   slideshowinteractor.SlideshowInteractor())
    
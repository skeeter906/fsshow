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

import wx
import util

class SlideshowInteractor(object):
    '''
    This class translates the low level events into the "higher level language" of the presenter
    '''
    def Install(self, presenter, view):
        self.presenter = presenter
        self.view = view
        view.app.Bind(wx.EVT_MENU, self._OnStartSlideshow, view.startSlideshowLink)
        view.app.Bind(wx.EVT_MENU, self._OnNextSlide, view.nextSlideLink)
        view.app.Bind(wx.EVT_MENU, self._OnPreviousSlide, view.previousSlideLink)
        view.app.Bind(wx.EVT_MENU, self._OnExitApp, view.exitLink)    
        view.app.Bind(wx.EVT_CHAR, self._OnKey)

    def _OnStartSlideshow(self, evt):
        """
        Handles the starting of the slideshow after clicking on the menu option.
        """
        util.debugLog("SlideshowInteractor._OnStartSlideshow()")
        self.presenter.StartSlideshow()
        
    def _OnNextSlide(self, evt):
        """
        Handles event to trigger the next slide.
        """
        util.debugLog("SlideshowInteractor._OnNextSlide()")
        self.presenter.ShiftSlide(blockTimer=True)
            
    def _OnPreviousSlide(self, evt):
        """
        Handles event to trigger the previous slide.
        """
        util.debugLog("SlideshowInteractor._OnPreviousSlide()")
        self.presenter.ShiftSlide(shift=-1, blockTimer=True)
            
    def StartTimer(self, waitSecs):
        """
        Initializes the timer in the presenter using wx.FutureCall.
        """
        util.debugLog("starting timer",2)
        self._timer = wx.FutureCall(waitSecs*1000, self.presenter.ShiftSlide)
        
    def StopTimer(self):
        if hasattr(self, "_timer"): self._timer.Stop()
        util.debugLog("stopping timer",2)
        
    def _OnExitApp(self, evt):
        """
        Handles the exit event.
        """        
        self.presenter.CleanupSlideshow()
        self.view.Close(True)

    def ToggleTimer(self):
        if hasattr(self, "_timer") and self._timer.IsRunning(): self.presenter.StopTimer()
        else: self.presenter.StartTimer()

    def _OnKey(self, evt):
        if evt.GetKeyCode() == wx.WXK_RIGHT:
            util.debugLog("wx.WXK_RIGHT",2)
            self.presenter.StopTimer()
            self.presenter.ShiftSlide(blockTimer=True)
        elif evt.GetKeyCode() == wx.WXK_LEFT:
            util.debugLog("wx.WXK_LEFT",2)
            self.presenter.StopTimer()
            self.presenter.ShiftSlide(shift=-1,blockTimer=True)
        elif evt.GetKeyCode() == wx.WXK_SPACE:
            util.debugLog("wx.WXK_SPACE",2)
            self.ToggleTimer()
        
        
        
    

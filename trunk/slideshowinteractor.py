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
        view.app.Bind(wx.EVT_MENU, self._OnStartTimer, view.startTimerLink)
        view.app.Bind(wx.EVT_MENU, self._OnNextSlide, view.nextSlideLink)
        
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
        self.presenter.ShowNextSlide(True)
        
    def _OnStartTimer(self, evt):
        """
        Handles event to trigger starting the timer.
        """
        util.debugLog("SlideshowInteractor._OnStartTimer()")
        self.presenter._SetTimer()
    
    def StartTimer(self, waitSecs=5):
        wx.FutureCall(waitSecs*1000, self.presenter.ShowNextSlide)
        
    
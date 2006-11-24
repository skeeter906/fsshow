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
import wx

class SlideshowView(wx.Frame):
    """
    Slideshow windowing system class, implemented with wxPython.
    """
    def __init__(self):
        self.app = wx.App(0)
        wx.Frame.__init__(self, None, -1, "fsshow", 
                          size=(800,600), style=wx.DEFAULT_FRAME_STYLE)
        
        self.SetBackgroundColour("black")
        
        self.CenterOnScreen()
        
        self.CreateStatusBar()
        
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        
        item = menu.Append(-1, "S&tart\tAlt-S", "Start Slideshow")
        self.app.Bind(wx.EVT_MENU, self._OnStartSlideshow, item)
        item = menu.Append(-1, "E&xit\tAlt-X", "Exit Test")
        self.app.Bind(wx.EVT_MENU, self._OnExitApp, item)
        
        menuBar.Append(menu, "&File")
        
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_CLOSE, self._OnCloseFrame)
        
        self._window = wx.Panel(self, -1)
        
        self._window.SetFocus()
        
    def _OnExitApp(self, evt):
        """
        Handles the exit event.
        """
        self.Close(True)
    
    def _OnCloseFrame(self, evt):
        """
        Handles the close frame event.
        """
        if hasattr(self, "window") and hasattr(self._window, "ShutdownDemo"):
            self._window.ShutdownDemo()
        evt.Skip()
        
    def _OnStartSlideshow(self, evt):
        """
        Handles the starting of the slideshow after clicking on the menu option.
        """
        util.debugLog("SlideshowView.OnStart()")
        
    def Start(self):
        '''
        Upon start we just show the frame and enter the MainLoop
        '''
        self.Show()
        self.app.MainLoop()

if __name__ == "__main__":
    view = SlideshowView()
    view.Start()
    
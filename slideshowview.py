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
        
        self.SetBackgroundColour("lightgray")
        
        #self.CenterOnScreen()
        
        self.CreateStatusBar()
        
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        
        self.startSlideshowLink = menu.Append(-1, "S&tart Slideshow\tAlt-S", "Start Slideshow")
        self.startTimerLink = menu.Append(-1, "Start T&imer\tAlt-T", "Start Timer")
        self.nextSlideLink = menu.Append(-1, "N&ext\tAlt-N", "Next Image")

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
        
    def Start(self):
        '''
        Upon start we just show the frame and enter the MainLoop
        '''
        self.Show()
        self.app.MainLoop()
        
    def ShowImage(self, imagePath):
        util.debugLog("slideshowview.ShowImage()")
        
        self.DestroyBmp()
        
        image = wx.Image(imagePath, wx.BITMAP_TYPE_JPEG)
        bmp = wx.BitmapFromImage(image)
        self._staticBmp = wx.StaticBitmap(self._window, wx.ID_ANY, bmp,
                                          wx.Point(0,0),
                                          wx.Size(image.GetWidth(),
                                                  image.GetHeight()))
        
    def DestroyBmp(self):
        util.debugLog("slideshowview.DestroyBmp()")
        if hasattr(self, "_staticBmp"): self._staticBmp.Destroy()
        

if __name__ == "__main__":
    view = SlideshowView()
    view.Start()
    
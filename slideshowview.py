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
import wx
import imaging
import os

class SlideshowView(wx.Frame):
    """
    Slideshow windowing system class, implemented with wxPython.
    """
    def __init__(self):
        self.app = wx.App(0)
        wx.Frame.__init__(self, None, -1, "fsshow", 
                          size=(800,600), style=(wx.DEFAULT_FRAME_STYLE))#|wx.MAXIMIZE))
        
        self._statusBar = self.CreateStatusBar()
        
        menuBar = wx.MenuBar()
        
        # Build the File menu
        filemenu = wx.Menu()
        item = filemenu.Append(-1, "&About\tAlt-A", "About")
        self.app.Bind(wx.EVT_MENU, self._OnAbout, item)
        filemenu.AppendSeparator()
        self.exitLink = filemenu.Append(-1, "E&xit\tAlt-X", "Exit")
        menuBar.Append(filemenu, "&File")

        # Build the Slideshow menu
        slidemenu = wx.Menu()
        self.startSlideshowLink = slidemenu.Append(-1, "S&tart Slideshow\tCtrl-S", "Start Slideshow")
        self.nextSlideLink = slidemenu.Append(-1, "N&ext\tRight", "Next Image")
        self.previousSlideLink = slidemenu.Append(-1, "P&revious\tLeft", "Previous Image")
        self.fullscreenLink = slidemenu.Append(-1, "F&ull Screen\tF11", "Toggle Full Screen")
        menuBar.Append(slidemenu, "&Slideshow")
        
        # Set the menus
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_CLOSE, self._OnCloseFrame)
        
        self._window = wx.Panel(self, -1)

        self._window.SetBackgroundColour("black")        
        
        self._window.SetFocus()
    
    def UpdateStatus(self, text):
        self._statusBar.SetStatusText(text)
        if text: self.SetTitle("fsshow - " + text)
        else: self.SetTitle(fsshow)
        
    def _OnCloseFrame(self, evt):
        """
        Handles the close frame event.
        """
        if hasattr(self, "_window") and hasattr(self._window, "ShutdownDemo"):
            self._window.ShutdownDemo()
        evt.Skip()
    
    def _OnAbout(self, evt):
        d = wx.MessageDialog(self, "fsshow\n"
                             "A full screen slideshow generator for Flickr.\n"
                             "Copyright (c) 2006 Mat Malone",
                             "About fsshow",
                             wx.OK)
        d.ShowModal()
        d.Destroy()        
    
    def OnFullscreen(self, evt):
        if not self.IsFullScreen(): show = True
        else: show = False
        self.ShowFullScreen(show, wx.FULLSCREEN_ALL)
    
    def Start(self):
        '''
        Upon start we just show the frame and enter the MainLoop
        '''
        self.Show()
        self.app.MainLoop()
        
    def ShowImage(self, imagePath):
        util.debugLog("slideshowview.ShowImage()")

        # added to fix problem with statusbar/title update not appearing
        wx.YieldIfNeeded()
        util.debugLog("ShowImage() YIELDING",2)
        
        # resize the image
        fitted = imaging.FitImage(imagePath)
        newImagePath = os.path.join("cache", "fit_" + os.path.basename(imagePath))
        imagePath = fitted.DownsizeFit(self._window.GetSize(), newImagePath)
        
        image = wx.Image(newImagePath, wx.BITMAP_TYPE_JPEG)
        
        x,y = imaging.GetCenterFromTopLeft(self._window.GetSize(), image.GetSize())
                
        bmp = wx.BitmapFromImage(image)
        self.DestroyBmp()
        self._staticBmp = wx.StaticBitmap(self._window, wx.ID_ANY, bmp,
                                          wx.Point(x,y),
                                          wx.Size(image.GetWidth(),
                                                  image.GetHeight()))

        try:
            os.unlink(newImagePath)
        except IOError, (errno, strerror):
            print "I/O error(%s): %s" % (errno, strerror)
        
        util.debugLog("ShowImage() done",2)
        
    def DestroyBmp(self):
        util.debugLog("slideshowview.DestroyBmp()")
        if hasattr(self, "_staticBmp"): self._staticBmp.Destroy()
    
    def Popup(self, msg, title="Attention"):
        d = wx.MessageDialog(self, msg, title, wx.OK)
        d.ShowModal()
        d.Destroy()                

if __name__ == "__main__":
    view = SlideshowView()
    view.Start()
    

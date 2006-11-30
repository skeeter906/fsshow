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

DEBUG_LEVEL = 1

import threading

def debugLog(msg, level=1):
    if level <= DEBUG_LEVEL: print "debug: " + msg

def getSearchParamType(s):
    if s.lower()[0:7] == "http://": return "url"
    elif s.find("@", 1, len(s)-1) >= 0: return "email"
    else: return "username"

def info(object, spacing=10, collapse=1):
    """Print methods and doc strings.
    
    Takes module, class, list, dictionary, or string."""
    methodList = [method for method in dir(object) if callable(getattr(object, method))]
    processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
    return "\n".join(["%s %s" %
                      (method.ljust(spacing),
                       processFunc(str(getattr(object, method).__doc__)))
                     for method in methodList])

class ThreadCounter(object):
    def __init__(self, n=0):
        self._n = n
        self._lock = threading.Lock()
        self._wasTouched = False
    def Add(self, x):
        self._lock.acquire()
        self._n += x
        self._lock.release()
        self._wasTouched = True
    def Up(self):
        self.Add(1)
    def Down(self):
        self.Add(-1)
    def Set(self, n):
        self._lock.acquire()
        self._n = n
        self._lock.release()
        self._wasTouched = True
    def Get(self):
        self._lock.acquire()
        n = self._n
        self._lock.release()
        return n
    def WasTouched(self): return self._wasTouched



if __name__ == "__main__":
    debugLog("testing debug", 10)
    
    print info(info)
    
    tc = ThreadCounter()
    tc.Set(3)
    tc.Up()
    tc.Down()
    tc.Down()
    print "tc = ", tc.Get()
    
    print getSearchParamType("http://www.asdf")
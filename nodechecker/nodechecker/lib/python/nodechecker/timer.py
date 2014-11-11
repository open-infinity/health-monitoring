#!/usr/bin/env python2

#
# Desc
#

from __future__ import division  # Python 3 forward compatibility
from __future__ import print_function  # Python 3 forward compatibility

import threading

class RepeatingTimer(threading.Thread):
    def __init__(self, interval, function, args=[], kwargs={}):
        threading.Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs 
        self.finished = threading.Event()

    def run(self):
       while True:
            print("waiting..........")
            self.finished.wait(self.interval)
            print("....not waiting")
            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
            else:
                break    
    def shutdown(self):
        print("..........finished")
        self.finished.set()

   
    





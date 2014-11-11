#!/usr/bin/env python2

#
# Desc
#

from __future__ import division  # Python 3 forward compatibility
from __future__ import print_function  # Python 3 forward compatibility
import logging
import sys
import os
import subprocess
import socket
import threading
import time
import functools

import util
import udp_listener


class RepeatingTimer(Thread):
    def __init__(self, a_context, function, args=[], kwargs={}):
        threading.Thread.__init__(self)
        self._ctx = a_context
        self._continue = Event()

    def run(self):
       while True:
            self._continue.wait(self._ctx.heartbeat_period)
            if not self._continue.is_set():
                self.function(*self.args, **self.kwargs)
    def shutdown(self):
        self._continue.set()

   
    





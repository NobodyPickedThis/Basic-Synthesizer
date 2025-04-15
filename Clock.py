import time
import math
from lib import consts

#Acts as "master phase" so that phase need not be tracked on each individual frequency
class Clock:
    def __init__(self, start_time: int = time()):
        self._start = start_time
    #Phase from 0 to 2pi
    def currentPhase(self):
        frac = time() % self._start
        return float(2 * math.pi * frac)
    #Sample from 0 to BITRATE
    def currentSample(self):
        frac = time() % self._start
        return int(frac * consts.BITRATE)
    #Sample from 0 to BUFFER_SIZE
    def currentBufferPosition(self):
        frac = time() % self._start
        return int(frac * consts.BUFFER_SIZE)
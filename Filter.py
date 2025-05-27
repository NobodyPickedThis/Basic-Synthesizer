import math
import numpy as np
from lib import consts

class Filter():
    def __init__(self, cutoff: int, type: str):
        # Set filter type
        self._type = ""
        match type:
            case consts.HI_CUT:
                self._type = consts.HI_CUT
            case consts.LOW_CUT:
                self._type = consts.LOW_CUT
            case _:
                raise Exception(ValueError)
        
        # Constrain cutoff
        self._cutoff = cutoff
        if cutoff > consts.MAX_FREQ:
            self._cutoff = consts.MAX_FREQ
        if cutoff < consts.MIN_FREQ:
            self._cutoff = consts.MIN_FREQ

        #Start with silence
        self._output = np.zeros(consts.BUFFER_SIZE, np.float64)

    def setCutoff(self, newCutoff: int = consts.CUTOFF):
        self._cutoff = newCutoff

    def use(self, signal):
        match self._type:
            case consts.HI_CUT:
                pass
            case consts.LOW_CUT:
                return self.lowCut(signal)
            case _:
                raise Exception(ValueError)

    def lowCut(self, input_signal: np.array) -> np.array:
        a = float(math.e ** ((-2 * math.pi * self._cutoff) / consts.BITRATE))
        self._output = ((1 - a) * input_signal) + (a * self._output)

        #print(f"a: {a}, output[0 - 10]: {self._output[:10]}, size of output: {len(self._output)}")

        return self._output

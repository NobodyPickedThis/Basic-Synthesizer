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

        # State variables
        self._in_prev = 0.0       # Used for low cut filter
        self._out_prev = 0.0      # Used for both high and low cut filter

        # Complicated math stuff abstracted into this function
        self._alpha = 0.001
        self.calculateCoefficients()

        # Effeciency
        match self._type:
            case consts.HI_CUT:
                self.use_type = self.hi_cut
            case consts.LOW_CUT:
                self.use_type = self.low_cut
            case _:
                raise Exception(ValueError)

    def setCutoff(self, newCutoff: int = consts.CUTOFF):
        self._cutoff = newCutoff
        if self._cutoff > consts.MAX_FREQ:
            self._cutoff = consts.MAX_FREQ
        if self._cutoff < consts.MIN_FREQ:
            self._cutoff = consts.MIN_FREQ
        self.calculateCoefficients()

    def calculateCoefficients(self):
        
        # Normalize cutoff freqency as a fraction of Nyquist frequency
        normalized_cutoff = self._cutoff / consts.NYQUIST

        # Disallow 0 or 1 to prevent unintended behaviour
        normalized_cutoff = max(0.001, min(0.999, normalized_cutoff))

        # Cookbook formulae implementation
        match self._type:
            case consts.HI_CUT:
                self._alpha = math.tan(math.pi * normalized_cutoff) / (1 + math.tan(math.pi * normalized_cutoff))
            case consts.LOW_CUT:
                self._alpha = 1.0 / (1 + math.tan(math.pi * normalized_cutoff))
            case _:
                raise Exception(ValueError)

        

    # Applies the appropriate filter to all samples of a buffer
    def use(self, input_signal: np.array) -> np.array:
        # Normalize
        normalized_input = input_signal.astype(np.float64) / 32767.0
        return (self.use_type(normalized_input) * 32767.0).astype(np.int16)

    def hi_cut(self, input_signal: np.array) -> np.array:
        output = np.zeros(consts.BUFFER_SIZE, np.float64)
        # Iterate through input buffer, applying filter
        for i in range(len(input_signal)):
            output[i] = self._alpha * input_signal[i] + (1 - self._alpha) * self._out_prev
            # Update state variables
            self._in_prev = input_signal[i]
            self._out_prev = max(-1.0, min(1.0, output[i]))
        return output
    
    def low_cut(self, input_signal: np.array) -> np.array:
        output = np.zeros(consts.BUFFER_SIZE, np.float64)
        # Iterate through input buffer, applying filter
        for i in range(len(input_signal)):
            output[i] = self._alpha * (self._out_prev + input_signal[i] - self._in_prev)
            # Update state variables
            self._in_prev = input_signal[i]
            self._out_prev = max(-1.0, min(1.0, output[i]))
        return output

        

        

import math
import numpy as np
from lib import consts

class Filter():
    def __init__(self):
        # Set filter type
        self._type = ""
        match consts.FILTER_TYPE:
            case consts.HI_CUT:
                self._type = consts.HI_CUT
            case consts.LOW_CUT:
                self._type = consts.LOW_CUT
            case _:
                raise Exception(ValueError)
        
        # Constrain cutoff and Q
        self._cutoff = consts.MAX_FILTER_FREQ
        self._Q = 0.707

        # State variables
        # Previous two inputs: x[n-1] and x[n-2]
        self._x1 = 0.0      
        self._x2 = 0.0
        # Previous two outputs: y[n-1] and y[n-2]
        self._y1 = 0.0    
        self._y2 = 0.0

        # Complicated math stuff abstracted into this function
        self._alpha = 0.001
        self.calculateCoefficients()
        self._new_coefficients = False

        #Old coefficients used for interpolation
        self._prev_b0, self._prev_b1, self._prev_b2, self._prev_a1, self._prev_a2 = self._b0, self._b1, self._b2, self._a1, self._a2

    def setCutoff(self, newCutoff: int = consts.MAX_FILTER_FREQ):
        #Update old coefficients
        self._prev_b0, self._prev_b1, self._prev_b2, self._prev_a1, self._prev_a2 = self._b0, self._b1, self._b2, self._a1, self._a2

        #Recalculate new ones
        self._cutoff = newCutoff
        if self._cutoff > consts.MAX_FILTER_FREQ:
            self._cutoff = consts.MAX_FILTER_FREQ
        if self._cutoff < consts.MIN_FILTER_FREQ:
            self._cutoff = consts.MIN_FILTER_FREQ
        self.calculateCoefficients()
        self._new_coefficients = True

    def setQ(self, newQ: int = consts.MAX_Q):
        #Update old coefficients
        self._prev_b0, self._prev_b1, self._prev_b2, self._prev_a1, self._prev_a2 = self._b0, self._b1, self._b2, self._a1, self._a2

        #Recalculate new ones
        self._Q = newQ
        if self._Q > consts.MAX_Q:
            self._Q = consts.MAX_Q
        if self._Q < consts.MIN_Q:
            self._Q = consts.MIN_Q
        self.calculateCoefficients()
        self._new_coefficients = True
    
    # Determines the behaviour of the filter
    def calculateCoefficients(self):
        # Normalize cutoff freqency, get Q 
        omega = 2.0 * math.pi * self._cutoff / consts.BITRATE
        sin_omega = math.sin(omega)
        cos_omega = math.cos(omega)
        alpha = sin_omega / (2 * self._Q)

        # The application of our filter no longer depends on filter types,
        # which are expressed by the coefficients. So we determine 
        # behaviour at this stage rather than during the use.
        if self._type == consts.HI_CUT: 
            self._b0 = (1.0 - cos_omega) / 2.0
            self._b1 = 1.0 - cos_omega
            self._b2 = (1.0 - cos_omega) / 2.0
            self._a0 = 1.0 + alpha  # Normalization factor
            self._a1 = -2.0 * cos_omega
            self._a2 = 1.0 - alpha
        
        elif self._type == consts.LOW_CUT:
            self._b0 = (1.0 + cos_omega) / 2.0
            self._b1 = -(1.0 + cos_omega)
            self._b2 = (1.0 + cos_omega) / 2.0
            self._a0 = 1.0 + alpha
            self._a1 = -2.0 * cos_omega
            self._a2 = 1.0 - alpha

        else:
            raise Exception(ValueError)

        # Normalize all coefficients by a0
        self._b0 /= self._a0
        self._b1 /= self._a0
        self._b2 /= self._a0
        self._a1 /= self._a0
        self._a2 /= self._a0

    # Applies the filter to all samples of a buffer
    def use(self, input_signal: np.array) -> np.array:
        # Normalize input to ±1.0
        normalized_input = input_signal.astype(np.float32) / 32767.0
        output = np.zeros(consts.BUFFER_SIZE, np.float32)

        # If coefficients have changed, use interpolation
        if self._new_coefficients:
            for i in range(consts.BUFFER_SIZE):

                # Interpolate coefficients for cleaner parameter modulation
                progress = i / consts.BUFFER_SIZE
                b0 = self._prev_b0 + (self._b0 - self._prev_b0) * progress
                b1 = self._prev_b1 + (self._b1 - self._prev_b1) * progress
                b2 = self._prev_b2 + (self._b2 - self._prev_b2) * progress
                a1 = self._prev_a1 + (self._a1 - self._prev_a1) * progress
                a2 = self._prev_a2 + (self._a2 - self._prev_a2) * progress

                current_input = normalized_input[i]

                # 2-pole biquad difference equation
                current_output = (b0 * current_input + 
                                b1 * self._x1 + 
                                b2 * self._x2 - 
                                a1 * self._y1 - 
                                a2 * self._y2)
            
                # Clamp output to prevent runaway
                current_output = max(-1.0, min(1.0, current_output))
                output[i] = current_output
                
                # Shift state variables
                self._x2 = self._x1
                self._x1 = current_input
                self._y2 = self._y1  
                self._y1 = current_output

            # Reset coefficient flag
            self._new_coefficients = False
        else:
            for i in range(consts.BUFFER_SIZE):
                current_input = normalized_input[i]

                # 2-pole biquad difference equation
                current_output = (self._b0 * current_input + 
                                self._b1 * self._x1 + 
                                self._b2 * self._x2 - 
                                self._a1 * self._y1 - 
                                self._a2 * self._y2)
            
                # Clamp output to prevent runaway
                current_output = max(-1.0, min(1.0, current_output))
                output[i] = current_output
                
                # Shift state variables
                self._x2 = self._x1
                self._x1 = current_input
                self._y2 = self._y1  
                self._y1 = current_output

        return (output * 32767.0).astype(np.int16)

        

        

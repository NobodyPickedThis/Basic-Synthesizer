import math
import numpy as np
import scipy
from scipy import signal

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

        # Interpolation constants
        self._samples_per_step = consts.BUFFER_SIZE // consts.INTERP_STEPS

        # State variables
        # Previous two inputs: x[n-1] and x[n-2]
        self._x1_L = 0.0      
        self._x2_L = 0.0
        self._x1_R = 0.0      
        self._x2_R = 0.0
        # Previous two outputs: y[n-1] and y[n-2]
        self._y1_L = 0.0    
        self._y2_L = 0.0
        self._y1_R = 0.0    
        self._y2_R = 0.0

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
            self._a0 = 1.0 + alpha  # Normalization factor
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
        output = np.empty((consts.BUFFER_SIZE, 2), dtype=np.float32)

        # If coefficients have changed, use interpolation
        if self._new_coefficients:

            for step in range(consts.INTERP_STEPS):

                # Interpolate coefficients for cleaner parameter modulation
                progress = (step + 1) / consts.INTERP_STEPS
                b0 = self._prev_b0 + (self._b0 - self._prev_b0) * progress
                b1 = self._prev_b1 + (self._b1 - self._prev_b1) * progress
                b2 = self._prev_b2 + (self._b2 - self._prev_b2) * progress
                a1 = self._prev_a1 + (self._a1 - self._prev_a1) * progress
                a2 = self._prev_a2 + (self._a2 - self._prev_a2) * progress

                i_0 = step * self._samples_per_step
                i_f = i_0 + self._samples_per_step
                
            
                # Interpolate rather than calculate every sample
                for i in range(i_0, i_f):

                    current_input_L = input_signal[i, 0]
                    current_input_R = input_signal[i, 1]

                    # 2-pole biquad difference equation
                    current_output_L = (b0 * current_input_L + 
                                    b1 * self._x1_L + 
                                    b2 * self._x2_L - 
                                    a1 * self._y1_L - 
                                    a2 * self._y2_L)
                    current_output_R = (b0 * current_input_R + 
                                    b1 * self._x1_R + 
                                    b2 * self._x2_R - 
                                    a1 * self._y1_R - 
                                    a2 * self._y2_R)
                    
                    # Clamp output to prevent runaway
                    current_output_L = max(-1.0, min(1.0, current_output_L))
                    output[i, 0] = current_output_L
                    current_output_R = max(-1.0, min(1.0, current_output_R))
                    output[i, 1] = current_output_R
                    
                    # Shift state variables
                    self._x2_L = self._x1_L
                    self._x1_L = current_input_L
                    self._y2_L = self._y1_L
                    self._y1_L = current_output_L
                    self._x2_R = self._x1_R
                    self._x1_R = current_input_R
                    self._y2_R = self._y1_R
                    self._y1_R = current_output_R

            # Reset coefficient flag
            self._new_coefficients = False
        else:

            b0, b1, b2, a1, a2 = self._b0, self._b1, self._b2, self._a1, self._a2

            for i in range(consts.BUFFER_SIZE):
                current_input_L = input_signal[i, 0]
                current_input_R = input_signal[i, 1]

                # 2-pole biquad difference equation
                current_output_L = (b0 * current_input_L + 
                                b1 * self._x1_L + 
                                b2 * self._x2_L - 
                                a1 * self._y1_L - 
                                a2 * self._y2_L)
                current_output_R = (b0 * current_input_R + 
                                b1 * self._x1_R + 
                                b2 * self._x2_R - 
                                a1 * self._y1_R - 
                                a2 * self._y2_R)
            
                # Clamp output to prevent runaway
                current_output_L = max(-1.0, min(1.0, current_output_L))
                output[i, 0] = current_output_L
                current_output_R = max(-1.0, min(1.0, current_output_R))
                output[i, 1] = current_output_R
                
                # Shift state variables
                self._x2_L = self._x1_L
                self._x1_L = current_input_L
                self._y2_L = self._y1_L 
                self._y1_L = current_output_L
                self._x2_R = self._x1_R
                self._x1_R = current_input_R
                self._y2_R = self._y1_R
                self._y1_R = current_output_R

        return output

    # For visualization
    def getFreqResponse(self) -> np.array:
        w, h = signal.freqz(b=[self._b0, self._b1, self._b2], a=[self._a0, self._a1, self._a2])
        h = np.real(h)
        return [w, h]
        

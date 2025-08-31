import numpy as np
import math



from lib import consts

# FIXME commented out debug statements to check efficiency

# See https://www.desmos.com/calculator/nrn6oabn6h for preliminary math

# Envelope generator object

class ADSR():

    def __init__(self, debug_mode: int = 0, attack: float = consts.ATTACK, decay: float = consts.DECAY, sustain: float = consts.SUSTAIN, release: float = consts.RELEASE):    # Attack, Decay, Release in s, Sustain 0.0 - 1.0

        # Parameter values
        self._attack = int(float(attack) * consts.BITRATE)
        self._decay = int(float(decay) * consts.BITRATE)
        self._sustain = sustain
        self._release = int(float(release) * consts.BITRATE )

        # Used to fade between values when envelope changes to release at unexpected time
        self._value = 0.0

        self._exp_release_coef = consts.EXPONENTIAL_DECAY_COEFFICIENT

        # Array initializations, ensure enough samples to prevent non-flat sustain and post-release buffers
        self._ADS_len = self._attack + self._decay
        if self._ADS_len < consts.BUFFER_SIZE:
            self._ADS_len += consts.BUFFER_SIZE % self._ADS_len
        self._ADS_values = np.zeros(self._ADS_len, dtype=float)        
        self._R_len = self._release
        if self._R_len < consts.BUFFER_SIZE:
            self._R_len += consts.BUFFER_SIZE % self._R_len
        self._R_values = np.zeros(self._R_len, dtype=float)                  

        # Array populations
        self.generateADS()
        self.generateR()
        self._empty_buffer = np.zeros(consts.BUFFER_SIZE, float)

        # Track which partition of envelope to use
        self._state = consts.OFF
        self._position = 0

        # Flag for dynamically updating parameters during runtime
        self._old_params = False

        self._debug_mode = debug_mode

    # Populate ADS array
    def generateADS(self):
        for i in range(self._ADS_values.size):

            # Attack segment
            if i < self._attack:
                self._ADS_values[i] = float(i / self._attack) ** 2      #Quadratic attack

            # Decay segment
            elif i < (self._attack + self._decay):
                #Decay progress
                decay_position = (i - self._attack) / self._decay
                # Linear value
                linear_value = (1 - decay_position) + (self._sustain * decay_position)
                # Apply exponential decay function based on coefficient
                self._ADS_values[i] = max(linear_value * math.e ** (- self._exp_release_coef * decay_position), self._sustain)

            # Sustain buffer
            else:
                self._ADS_values[i] = self._sustain

    # Populate R values
    def generateR(self):
        
        safety_sustain = max(self._sustain, 0.00000000001)

        for i in range(self._R_values.size):

            # Release segment
            if i < self._release:
                # Linear value
                self._R_values[i] = ((-safety_sustain / self._release) * i + safety_sustain)
                # Apply exponential decay function based on coefficient
                self._R_values[i] =  self._R_values[i] * math.e ** (- self._exp_release_coef * (i / self._release))

            # Silence buffer
            else:
                self._R_values[i] = 0.0

    # Return envelope data, increment buffer chunk
    def applyEnvelope(self, pre_env_data):

        return_data = self._empty_buffer

        match self._state:
            case consts.ADS:
                for i in range(consts.BUFFER_SIZE):

                    pos = self._position + i
                    if pos < self._ADS_len:
                        env_val = self._ADS_values[pos]
                    else:
                        env_val = self._sustain
                        
                    return_data[i] = pre_env_data[i] * env_val
                
                self._value = env_val    
                self._position += consts.BUFFER_SIZE
                return return_data

            case consts.R:

                #Prevent math issues when sustain is 0
                scale_factor = self._value / max(self._sustain, 0.00000000001)

                for i in range(consts.BUFFER_SIZE):
                    pos = self._position + i
                    if pos < self._release:
                        return_data[i] = pre_env_data[i] * scale_factor * self._R_values[pos]    # This should be sustain if note was held long enough before
                                                                                                 # release, if not then this is the value it was at prior to release
                    else:
                        return_data[i] = 0.0

                self._position += consts.BUFFER_SIZE

                # Turn off envelope if complete
                if self._position >= self._release:
                    self.reset()
                    return np.zeros(consts.BUFFER_SIZE, float)

                return return_data

            case _:
                return return_data

    # Turn note on
    def start(self):
        #if self._debug_mode == 2:
        #    print("Envelope state before start: ", self._state)
        self._state = consts.ADS
        #if self._debug_mode == 2:
        #    print("Envelope state after start: ", self._state)
    # Change state from ADS to R, turn off if release is 0 immediately
    def release(self):
        if self._state == consts.ADS:
            #Capture current envelope value
            if self._position < self._ADS_len:
                self._value = self._ADS_values[self._position]
            else:
                self._value = self._sustain

            #Switch state, resetting position
            self._state = consts.R
            self._position = 0

    # Check state
    def isOn(self) -> bool:
        return self._state == consts.ADS or self._state == consts.R
    def isOff(self) -> bool:
        return self._state == consts.OFF

    # Reset envelope to initial state (for after it has been "used up")
    def reset(self):
        #if self._debug_mode == 2:
        #    print("Envelope state before reset: ", self._state)
        if self._old_params:
            self._ADS_values = np.zeros(self._ADS_len, dtype=float)
            self._R_values = np.zeros(self._R_len, dtype=float) 
            self.generateADS()
            self.generateR()
        self._state = consts.OFF
        self._position = 0
        self._value = 0.0
        #if self._debug_mode == 2:
        #    print("Envelope state after reset: ", self._state)

    # Visualize envelope
    def drawEnvelope(self, plot, pos: int = 1) -> None:
        #Slightly modifying lists to reduce "flat" sections between decay and release and release and end
        plot.drawWaveform(np.concatenate((self._ADS_values, self._R_values)), pos)
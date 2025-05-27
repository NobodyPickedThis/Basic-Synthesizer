import numpy as np



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

        # Track which partition of envelope to use
        self._state = consts.OFF
        self._position = 0

        self._debug_mode = debug_mode

    # Populate ADS array
    def generateADS(self):
        for i in range(self._ADS_values.size):

            # Attack segment
            if i < self._attack:
                self._ADS_values[i] = float(i / self._attack) ** 2      #Quadratic attack

            # Decay segment
            elif i < (self._attack + self._decay):
                self._ADS_values[i] = (((self._sustain - 1) * (i - self._attack)) / float(self._decay)) + 1

            # Sustain buffer
            else:
                self._ADS_values[i] = self._sustain

    # Populate R values
    def generateR(self):
        
        for i in range(self._R_values.size):

            # Release segment
            if i < self._release:
                self._R_values[i] = ((-self._sustain / self._release) * i + self._sustain)

            # Silence buffer
            else:
                self._R_values[i] = 0.0

    # Return envelope data, increment buffer chunk
    def applyEnvelope(self, pre_env_data):

        arr_size = len(pre_env_data)
        return_data = np.zeros(arr_size, float)

        match self._state:
            case consts.ADS:
                for i in range(arr_size):

                    pos = self._position + i
                    if pos < self._attack:
                        env_val = float(pos / self._attack) ** 2
                    elif pos < (self._attack + self._decay):
                        env_val = (((self._sustain - 1) * (pos - self._attack)) / float(self._decay)) + 1
                    else:
                        env_val = self._sustain
                        
                    return_data[i] = pre_env_data[i] * env_val
                    self._value = env_val
                    
                self._position += arr_size
                return return_data

            case consts.R:
                for i in range(arr_size):
                    
                    pos = self._position + i
                    if pos < self._release:
                        return_data[i] = pre_env_data[i] * self._R_values[pos] * self._value    # This should be sustain if note was held long enough before
                                                                                                # release, if not then this is the value it was at prior to release
                    else:
                        return_data[i] = 0.0

                self._position += arr_size

                # Turn off envelope if complete
                if self._position >= self._release:
                    self.reset()
                    return np.zeros(arr_size, float)

                return return_data

            case _:
                return return_data

    # Turn note on
    def start(self):
        #if self._debug_mode > 1:
        #    print("Envelope state before start: ", self._state)
        self._state = consts.ADS
        #if self._debug_mode > 1:
        #    print("Envelope state after start: ", self._state)
    # Change state from ADS to R, turn off if release is 0 immediately
    def release(self):
        #if self._debug_mode > 1:
        #    print("Envelope state before release: ", self._state)
        if self._state == consts.ADS:
            self._state = consts.R
            self._position = 0
        #if self._debug_mode > 1:
        #    print("Envelope state after release: ", self._state)

    # Check state
    def isOn(self) -> bool:
        return self._state == consts.ADS or self._state == consts.R
    def isOff(self) -> bool:
        return self._state == consts.OFF

    # Reset envelope to initial state (for after it has been "used up")
    def reset(self):
        #if self._debug_mode > 1:
        #    print("Envelope state before reset: ", self._state)
        self._ADS_values = np.zeros(self._ADS_len, dtype=float)
        self._R_values = np.zeros(self._R_len, dtype=float) 
        self.generateADS()
        self.generateR()
        self._state = consts.OFF
        self._position = 0
        #if self._debug_mode > 1:
        #    print("Envelope state after reset: ", self._state)

    # Visualize envelope
    def drawEnvelope(self, plot, pos: int = 1) -> None:
        #Slightly modifying lists to reduce "flat" sections between decay and release and release and end
        plot.drawWaveform(np.concatenate((self._ADS_values, self._R_values)), pos)
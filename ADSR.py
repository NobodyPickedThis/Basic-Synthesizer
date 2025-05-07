import numpy as np

from lib import consts
import Waveform_Visualizer

# See https://www.desmos.com/calculator/nrn6oabn6h for preliminary math
# Envelope generator object
class ADSR():
    def __init__(self, attack: int = 1000, decay: int = 1000, sustain: float = 1.0, release: int = 1000):    # Attack, Decay, Release in ms, Sustain 0.0 - 1.0
        
        # Parameter values
        self._attack = int(float(consts.MS_PER_SECOND * attack) / consts.BITRATE)
        self._decay = int(float(consts.MS_PER_SECOND * decay) / consts.BITRATE)
        self._sustain = sustain
        self._release = int(float(consts.MS_PER_SECOND * release) / consts.BITRATE )

        # Array initializations, ensure enough samples to prevent non-flat sustain and post-release buffers
        self._ADS_len = consts.BUFFER_SIZE + self._attack + self._decay
        self._ADS_values = np.zeros(self._ADS_len, dtype=float)        
        self._R_len = consts.BUFFER_SIZE + self._release
        self._R_values = np.zeros(self._R_len, dtype=float)                  

        # Array populations
        self.generateADS()
        self.generateR()

        # Track which partition of envelope to use
        self._state = consts.NOTE_ON

    # Populate ADS array
    def generateADS(self):
        for i in range(self._ADS_values.size):

            # Attack segment
            if i < self._attack:
                self._ADS_values[i] = float(i / self._attack)

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
                self._R_values[i] = (-self._sustain / self._release) * i + self._sustain

            # Silence buffer
            else:
                self._R_values[i] = 0.0

    # Return envelope data, increment buffer chunk
    def applyEnvelope(self, pre_env_data: np.array) -> np.array:
        
        arr_size = len(pre_env_data)
        
        #FIXME don't adjust values if they're already at their end state!
        match self._state:
            case consts.NOTE_ON:

                return_data = np.zeros(arr_size, float)

                for i in range(arr_size):
                    return_data[i] = pre_env_data[i] * self._ADS_values[i]
                
                if self._ADS_values[0] != self._sustain:
                    self._ADS_values = self._ADS_values[min(arr_size, 1):]

                return return_data

            case consts.NOTE_OFF:

                return_data = np.zeros(arr_size, float)

                for i in range(arr_size):
                    return_data[i] = max(0, pre_env_data[i] * self._R_values[i])
                
                if self._R_values[0] != 0:
                    self._R_values = self._R_values[min(arr_size, 1):]

                return return_data

        

    # Turn note on or off
    def on(self):
        self._state = consts.NOTE_ON
    def off(self):
        self._state = consts.NOTE_OFF

    # Reset envelope to initial state (for after it has been "used up")
    def reset(self):
        self._ADS_values = np.zeros(self._ADS_len, dtype=float)
        self._R_values = np.zeros(self._R_len, dtype=float) 
        self.generateADS()
        self.generateR()
        self._state = consts.NOTE_ON

    # Visualize envelope
    def drawEnvelope(self) -> None:
        #Slightly modifying lists to reduce "flat" sections between decay and release and release and end
        Waveform_Visualizer.drawWaveform(np.concatenate((self._ADS_values[:self._R_values.size - int(consts.BUFFER_SIZE / 2)], self._R_values[:self._R_values.size - consts.BUFFER_SIZE + 10])))
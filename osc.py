import math
import consts
import numpy as np

class RingBuffer:
    def __init__(self, size):
        self._size = size
        self._data = [0] * size
        self._index = 0
        self._is_full = False
        
    def add(self, value):
        self._data[self._index] = value
        self._index = (self._index + 1) % self._size
        if self._index == 0:
            self._is_full = True
            
    def get(self):
        if not self._is_full:
            return self._data[:self._index]
        return self._data[self._index:] + self._data[:self._index]
        
    def get_n(self, n):
        data = self.get()
        result = []
        while len(result) < n:
            result.extend(data)
        return result[:n]
    

class osc:
    def __init__(self, frequency = 200, wave_type = "Sine", amplitude: float = 1.0):
        #User defined parameters
        self._frequency = frequency
        self._wave_type = wave_type
        self._amplitude = amplitude
        self._bitrate = consts.BITRATE

        #Track phase for smooth audio between callback calls
        self._current_phase = 0

        #Generate wavedata
        self._period = float(1.0 / self._frequency)
        self._samples_per_period = int(math.floor(self._period * self._bitrate))

    #Generate phase-continuous samples
    def getWavedata(self, n_samples: int = consts.BUFFER_SIZE) -> list:
        # Create enough samples to fill the requested buffer size
        samples = np.zeros(n_samples, dtype=float)
        
        #Generate correct sample for specified parameters
        for i in range(n_samples):
            match self._wave_type:
                case "Sine":
                    samples[i] = self._amplitude * math.sin(self._current_phase)
                case "Square":
                    pass
                case "Saw":
                    pass
                case _:
                    pass

            #Advance phase, keep within reasonable range
            self._current_phase += (2 * math.pi * self._frequency) / consts.BITRATE
            if self._current_phase > 2 * math.pi:
                self._current_phase -= 2 * math.pi

        # Normalize to -1 to 1 range
        max_val = np.max(np.abs(samples))
        if max_val > 0:
            samples = samples / max_val
            
        # Convert to 8-bit audio (-128 to 127)
        samples_int8 = (samples * 127).astype(np.int8)
        
        return samples_int8
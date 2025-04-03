import math
import consts
import numpy as np
import Waveform_Visualizer

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
        samples[0] = 0
        
        #Generate correct sample for specified parameters
        for i in range(1, n_samples):
            match self._wave_type:
                case "Sine":
                    samples[i] = self._amplitude * math.sin(self._current_phase)

                case "Square":
                    if i % self._samples_per_period <= math.floor(self._samples_per_period / 2):
                        samples[i] = 1 * self._amplitude
                    else:
                        samples[i] = -1 * self._amplitude

                case "Saw":
                    samples[i] = self._amplitude - (2 * ((i % self._samples_per_period) / self._samples_per_period))

                case _:
                    pass

            #Advance phase, keep within reasonable range
            self._current_phase += (2 * math.pi * self._frequency) / consts.BITRATE
            if self._current_phase > 2 * math.pi:
                self._current_phase -= 2 * math.pi
            
        # Convert to 16-bit audio
        samples_int16 = (samples * 32767).astype(np.int16)
        
        return samples_int16
    
    def draw_wave(self) -> None:
        Waveform_Visualizer.drawWaveform(self.getWavedata(self._samples_per_period))
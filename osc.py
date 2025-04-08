import math
import consts
import numpy as np
import Waveform_Visualizer

class osc:
    def __init__(self, frequency: float = 200.0, wave_type = "Sine"):
        #User defined parameters
        self._frequency = frequency
        self._wave_type = wave_type
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
        for i in range(0, n_samples):
            match self._wave_type:
                case "Sine":
                    samples[i] = math.sin(self._current_phase)

                case "Square":
                    if self._current_phase < math.pi:
                        samples[i] = 1
                    else:
                        samples[i] = -1

                case "Saw":
                    samples[i] = 1 - (2 * (self._current_phase / (2 * math.pi)) - 1.0)

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

    def print_wave(self) -> None:
        print_list = self.getWavedata(self._samples_per_period)
        for x in print_list:
            print(x, end=" ")
        print()

    def update_wave(self, new_frequency: float = -1.0, new_wave_type = "Empty"):
        if not math.isclose(new_frequency, -1.0, rel_tol=1e-5):
            self._frequency = new_frequency
        if new_wave_type != "Empty":
            self._wave_type = new_wave_type
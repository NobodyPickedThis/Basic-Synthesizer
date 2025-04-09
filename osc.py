import math
from lib import consts
from lib import mtof
import numpy as np
import Waveform_Visualizer

class osc:
    def __init__(self, wave_type = "Sine"):

        #Constant parameters
        self._wave_type = wave_type

        #Dictionary to hold wavedata
        self._bank = dict()
        self._mtof = mtof.mtof()

        #Track phase for smooth audio between callback calls
        self._current_phase = 0

        #Initialize wavedata
        for i in range(21, 109):
            frequency = self._mtof[i]
            period = float(1.0 / frequency)
            samples_per_period = int(math.floor(period * consts.BITRATE))
            self._bank[i] = self.generateWavedata(samples_per_period, frequency, i)


    #Generate phase-continuous samples
    def generateWavedata(self, n_samples: int = consts.BUFFER_SIZE, frequency: float = 200.00, MIDI: int = 0) -> list:
        
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
            self._current_phase += (2 * math.pi * frequency) / consts.BITRATE
            if self._current_phase > 2 * math.pi:
                self._current_phase -= 2 * math.pi

            
        # Convert to 16-bit audio
        samples_int16 = (samples * 32767).astype(np.int16)
        
        return samples_int16
    
    #Return enough samples to fill the buffer size
    def __getitem__(self, MIDI_value) -> list:
        return_data = np.repeat(self._bank[MIDI_value], np.size(self._bank[MIDI_value]) / consts.BUFFER_SIZE)

        #Update phase: ratio of remainder after filling return data to samples per period, scaled from 0 to 2pi
        #FIXME check math and debug, I gotta go to work
        self._current_phase += ((np.size(self._bank[MIDI_value]) % consts.BUFFER_SIZE) / int(math.floor((1 / self._mtof[MIDI_value]) * consts.BITRATE))) * 2 * math.pi
        if self._current_phase > 2 * math.pi:
            self._current_phase -= 2 * math.pi

        return return_data
    
    def drawWave(self) -> None:
        Waveform_Visualizer.drawWaveform(self.getWavedata(self._samples_per_period))

    def printWave(self) -> None:
        print_list = self.getWavedata(self._samples_per_period)
        for x in print_list:
            print(x, end=" ")
        print()

    def updateWave(self, new_frequency: float = -1.0, new_wave_type = "Empty"):
        if not math.isclose(new_frequency, -1.0, rel_tol=1e-5):
            self._frequency = new_frequency
        if new_wave_type != "Empty":
            self._wave_type = new_wave_type
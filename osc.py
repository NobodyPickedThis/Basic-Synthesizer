import math
import time
import Clock
import Waveform_Visualizer
from lib import consts
from lib import mtof
import numpy as np

class osc:
    def __init__(self, wave_type = "Sine", clock_start: int = time.time()):

        #Constant parameters
        self._wave_type = wave_type
        self._mtof = mtof.mtof()
        self._clock = Clock.Clock(clock_start)

        #Dictionary to hold wave and phase data
        self._bank = dict()

        #Initialize wavedata
        for i in range(21, 109):
            frequency = self._mtof[i]
            samples_per_period = int(round(consts.BITRATE / frequency))

            #Generate 4 periods per note
            self._bank[i] = self.generateWavedata(samples_per_period, frequency)


    #Generate phase-continuous samples
    def generateWavedata(self, num_samples: int = 1, frequency: float = 1) -> np.array:
        
        # Create enough samples to fill the requested buffer size
        samples = np.zeros(num_samples, dtype=float)

        #NOT the position as used for audio output, this tracks generation progress
        generation_phase = 0.0
        
        #Generate correct sample for specified parameters
        for i in range(0, num_samples):

            match self._wave_type:
                case "Sine":
                    samples[i] = math.sin(generation_phase)

                case "Square":
                    if generation_phase < math.pi:
                        samples[i] = 1
                    else:
                        samples[i] = -1

                case "Saw":
                    samples[i] = 1 - (2 * (generation_phase / (2 * math.pi)) - 1.0)

                case _:
                    pass

            #Advance phase, keep within reasonable range FIXME is the range adjustment necessary?
            generation_phase += (2 * math.pi * frequency) / consts.BITRATE
            if generation_phase > 2 * math.pi:
                generation_phase -= 2 * math.pi

        #Scale and convert to int16
        int16_samples = (samples * 32767).astype(np.int16)
        return int16_samples
    
    #Returns the data in the index requested
    def __getitem__(self, MIDI_value) -> np.array:
        return self._bank[MIDI_value]
    
    def drawWave(self) -> None:
        Waveform_Visualizer.drawWaveform(self._bank[60])

    def printWave(self) -> None:
        print_list = self.getWavedata(self._samples_per_period)
        for x in print_list:
            print(x, end=" ")
        print()
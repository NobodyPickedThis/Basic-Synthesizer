import math

class osc:
    def __init__(self, frequency = 200, wave_type = "Sine", bitrate: int = 44100, amplitude: float = 1.0, phase: float = 0.0):
        #User defined parameters
        self._frequency = frequency
        self._osc_type = wave_type
        self._amplitude = amplitude
        self._phase = phase
        self._bitrate = bitrate

        #Generate wavedata
        self._period = float(1.0 / self._frequency)
        self._samples_per_period = int(math.floor(self._period * self._bitrate))
        self._wavedata = []
        match self._osc_type:
            case "Sine":
                self.sine()

            case "Square":
                self.square()

            case "Saw":
                self.saw()

    def sine(self):
        for x in range(0, self._samples_per_period):
            self._wavedata.append(self._amplitude * math.sin(((x * 2 * math.pi) - self._phase) / self._samples_per_period))

    def square(self):
        pass

    def saw(self):
        pass

    def getWavedata(self) -> list:
         # Create a copy for normalization
        normalized_wave = self._wavedata
        
        # Normalize to range -1 to 1 if not already
        max_val = abs(max(normalized_wave))
        if max_val > 0:
            normalized_wave = [(x / max_val) for x in normalized_wave]
            
        # Scale to range -128 to 127
        normalized_wave = [int(math.floor((x * 127))) for x in normalized_wave]
        
        # Convert to list and return
        return normalized_wave

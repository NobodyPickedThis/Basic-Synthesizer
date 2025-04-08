
#Calculation function, can call when latency isn't first priority
def mtof_calc(MIDI: int = -1) -> float: #default to A0
    
    #Don't convert non-note MIDI information
    if MIDI < 21 or MIDI > 108:
        raise ValueError("Only MIDI values between 21 and 108 (inclusive) have a frequency representation")
    
    #Convert based on fixed point A4 = MIDI 69 = 440Hz
    return 440 * (2 ** ((MIDI - 69) / 12))

#Object containing MIDI mappings. Create before latency is required, then reference as needed
class mtof():

    #Init by populating dictionary
    def __init__(self):
        self._dictionary = dict()
        for i in range(0, 21):
            self._dictionary[i] = False
        for i in range(21, 109):
            self._dictionary[i] = mtof_calc(i)
        for i in range(109, 128):
            self._dictionary[i] = False
    
    #Subscript operator []
    def __getitem__(self, key):
        return self._dictionary[key]
    
    #Debug / Reference
    def printAllMTOF(self):
        for i in range(21, 109):
            print("MIDI: ", i, ", frequency: ", f'{self._dictionary[i]:.5}', sep="")

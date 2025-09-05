from lib import consts
import numpy as np

# Allows communication between MIDI messages and their associated parameters.
class Parameter_Interface:

    def __init__(self):
        self._new_cutoff = None
        self._new_Q = None

        # Dictionaries to hold the values matching each MIDI cc to avoid calculation during runtime
        self._cutoff_bank = dict()
        self._Q_bank = dict()
        for i in range(0, consts.MAX_MIDI + 1):
            self._cutoff_bank[i] = self.generateCutoff(i)
            self._Q_bank[i] = self.generateQ(i)

    # Update the associated object with new parameters
    def handle_cc_message(self, cc_number, cc_value):

        match cc_number:
            case consts.CUTOFF_CC:
                
                self._new_cutoff = self._cutoff_bank[cc_value]

                if consts.DEBUG_MODE == 2:
                    print(f"Updating cutoff with new frequency: {self._new_cutoff}")

            case consts.Q_CC:
                
                self._new_Q = self._Q_bank[cc_value]

                if consts.DEBUG_MODE == 2:
                    print(f"Updating resonance: {self._new_Q}")

    # Generate cutoff values from MIDI values
    def generateCutoff(self, MIDI_value: int = 0):

        #Scale down initial value from 0 to 1
        x = max(0.001, min((MIDI_value / consts.MAX_MIDI), 0.999))

        #Coefficients
        a = (((np.log(x / (1 - x))) / (2 * np.e)) + 0.5) / 3
        b = max((0.63 * (x ** 2)), (consts.MIN_FILTER_FREQ / consts.MAX_FILTER_FREQ))
        c = np.sqrt(max(x - 0.80, 0.0001))
        A = 1 if x >= 0.5 else (x / (abs(x - 1)))
        B = 0 if x >= 0.5 else ((-x) / (abs(x - 1))) + 1
        C = 0 if x < 0.80 else (5 * abs(0.8 - x)) * (5 * (x - 1) + 5 * (((np.log(0.8 / (1 - 0.8))) / (2 * np.e)) + 0.5) / 3)

        if consts.DEBUG_MODE == 2 and MIDI_value == 60:
            print(f"Coefficients for MIDI value {MIDI_value}: a={a}, b={b}, c={c}, A={A}, B={B}, C={C}")

        fractional_cutoff = min(A * a + B * b + C * c, 1)
        return fractional_cutoff * consts.MAX_FILTER_FREQ 

    # Generate Q values from MIDI values
    def generateQ(self, MIDI_value: int = 0):
        return consts.MIN_Q + (MIDI_value / consts.MAX_MIDI) * (consts.MAX_Q - consts.MIN_Q)
        
    
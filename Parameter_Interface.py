from lib import consts

# Allows communication between MIDI messages and their associated parameters.
class Parameter_Interface:

    def __init__(self):
        #FIXME should these be here or in consts?
        self._new_cutoff = None
        self._cutoff_offset = 13
        self._cutoff_exp = 3
        self._new_Q = None
        self._Q_offset = 0
        self._Q_exp = 1

    # Used to create more useful curves from 0 to 20000, as linear computation isn't "natural sounding"
    def sigmoid(self, x: int = 0, offset: int = 0, exp: int = 1):
        return (((x - offset) / consts.MAX_MIDI) / (1 + abs((x - offset) / consts.MAX_MIDI))) ** exp

    # Update the associated object with new parameters
    def handle_cc_message(self, cc_number, cc_value):

        
        match cc_number:
            case consts.CUTOFF_CC:
                
                sigmoid_cutoff = self.sigmoid(cc_value, self._cutoff_offset, self._cutoff_exp)
                sigmoid_normalizer = 1.0 / (self.sigmoid(consts.MAX_MIDI) + self.sigmoid(0))
                scaled_cutoff = ((sigmoid_cutoff + abs(self.sigmoid(0))) * sigmoid_normalizer) * consts.MAX_FREQ
                self._new_cutoff = int(scaled_cutoff)

                if consts.DEBUG_MODE == 2:
                    print(f"Updating cutoff with new frequency: {self._new_cutoff}")

            case consts.Q_CC:
                
                sigmoid_Q = self.sigmoid(cc_value, self._Q_offset, self._Q_exp)
                sigmoid_normalizer = 1.0 / (self.sigmoid(consts.MAX_MIDI) + self.sigmoid(0))
                scaled_Q = ((sigmoid_Q + abs(self.sigmoid(0))) * sigmoid_normalizer) * consts.MAX_Q
                self._new_Q = scaled_Q

                if consts.DEBUG_MODE == 2:
                    print(f"Updating resonance: {self._new_Q}")

    
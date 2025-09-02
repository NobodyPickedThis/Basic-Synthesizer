from lib import consts

# Allows communication between MIDI messages and their associated parameters.
class Parameter_Interface:

    def __init__(self):
        self._new_cutoff = None
        self._cutoff_offset = 13
        self._cutoff_exp = 3

    # Used to create more useful curves from 0 to 20000, as linear computation isn't "natural sounding"
    def sigmoid(self, x: int = 0):
        return (((x - self._cutoff_offset) / consts.MAX_MIDI) / (1 + abs((x - self._cutoff_offset) / consts.MAX_MIDI))) ** self._cutoff_exp

    # Update the associated object with new parameters
    def handle_cc_message(self, cc_number, cc_value):

        
        match cc_number:
            case consts.CUTOFF_CC:
                
                sigmoid_cutoff = self.sigmoid(cc_value)
                sigmoid_normalizer = 1.0 / (self.sigmoid(consts.MAX_MIDI) + self.sigmoid(0))
                scaled_cutoff = ((sigmoid_cutoff + abs(self.sigmoid(0))) * sigmoid_normalizer) * consts.MAX_FREQ
                self._new_cutoff = int(scaled_cutoff)

                if consts.DEBUG_MODE == 2:
                    print(f"Updating cutoff with new frequency: {self._new_cutoff}")

    
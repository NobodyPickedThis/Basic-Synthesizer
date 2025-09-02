from lib import consts

# Allows communication between MIDI messages and their associated parameters.
class Parameter_Interface:

    def __init__(self):
        self._new_cutoff = None
        self._min = 0
        self._max = 20000

    # Update the associated object with new parameters
    def handle_cc_message(self, cc_number, cc_value):
        match cc_number:
            case consts.CUTOFF_CC:
                self._new_cutoff = min(max(int((cc_value / 127.0) * (consts.MAX_FREQ - consts.MIN_FREQ) + consts.MIN_FREQ), self._min), self._max)
                if consts.DEBUG_MODE == 2:
                    print(f"Updating cutoff with new frequency: {self._new_cutoff}")
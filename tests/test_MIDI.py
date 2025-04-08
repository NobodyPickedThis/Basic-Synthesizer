from .. import mtof
from .. import MIDI_input as MIDI
import time

#mtof calls:
#test_mtof = mtof.mtof()
#test_mtof.printAllMTOF()

#MIDI_input calls:
test_MIDI = MIDI.MIDI_device()

#Hack to let me test MIDI stream
while True:
    time.sleep(1)
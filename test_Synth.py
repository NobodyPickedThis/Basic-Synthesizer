from lib import mtof
import MIDI_input as MIDI
import Synth
import time

#mtof calls:
#test_mtof = mtof.mtof()
#test_mtof.printAllMTOF()

#mton calls:
#test_mton = mtof.mton()
#test_mton.printAllMTON()

#test_MIDI = MIDI.MIDI_device()

#Synth calls
test_Synth = Synth.Synth(2)
test_Synth.printAllMIDIDevices()

print("Connected to MIDI input:", test_Synth._device_is_connected)

#Hack to let me test MIDI objects
while True:
    time.sleep(1)
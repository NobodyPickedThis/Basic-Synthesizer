from lib import mtof
import MIDI_input as MIDI
import Synth
import time
import numpy as np

#mtof calls:
#test_mtof = mtof.mtof()
#test_mtof.printAllMTOF()

#mton calls:
#test_mton = mtof.mton()
#test_mton.printAllMTON()

#test_MIDI = MIDI.MIDI_device()

#Synth calls
test_Synth = Synth.Synth("Saw", 2)
test_Synth.printAllMIDIDevices()
#test_Synth.printSoundBank()
test_Synth.printActiveVoices()

print("Connected to MIDI input:", test_Synth._device_is_connected)



#FIXME spoof some MIDI signals
test_Synth._output.play(test_Synth._soundbank[60])
time.sleep(0.5)
test_Synth._output.play((test_Synth._silence * 32767).astype(np.int16))
time.sleep(0.5)
test_Synth._output.play(test_Synth._soundbank[72])
time.sleep(0.5)
test_Synth._output.play((test_Synth._silence * 32767).astype(np.int16))

#Hack to let me test with MIDI devices
#while True:
#    time.sleep(1)
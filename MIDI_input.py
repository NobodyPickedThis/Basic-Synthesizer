import pygame.midi as MIDI
import string

#Handles input from MIDI devices, translating MIDI info into note-on, note-off, frequency, and velocity values
class MIDI_Device:
    def __init__(self):
        MIDI.init()
        self._controllerID = self.ConnectController()


    def __del__(self):
        MIDI.quit()

    def connectController(self) -> string:
        return 



class test_MIDI:
    def __init__(self):
        MIDI.init()
        self.printAllMIDIDevices()

    def __del__(self):
        MIDI.quit()

    def printAllMIDIDevices(self):
        for i in range(MIDI.get_count()):
            print(MIDI.get_device_info(i), i)
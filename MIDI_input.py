import pygame.midi as MIDI

#Handles input from MIDI devices, translating MIDI info into note-on, note-off, frequency, and velocity values
class MIDI_Device:
    def __init__(self):
        MIDI.init()


    def __del__(self):
        MIDI.quit()
import numpy as np
import time

import MIDI_input as MIDI
import Output_Stream
import osc
import ADSR
#import filter
from lib import mtof
from lib import consts

UNUSED = -1

#"Hub" class, defines signal flow up until Output_Stream
#   -IS A MIDI_device object
#   -HAS A(N) oscillator (osc)
#   -         envelope (ADSR)     see https://www.desmos.com/calculator/nrn6oabn6h for math
#   -         Filter (Filter)
#
class Synth(MIDI.MIDI_device):
    def __init__(self, wave_type: str = consts.WAVE_TYPE, debug_mode: int = 0, amplitude: float = 1.0):
        
        super().__init__(consts.DEVICE_NAME)
        
        self._debug_mode = debug_mode #0 --- No debug outputs
                                      #1 --- Simple debug outputs
                                      #2 --- Verbose debug outputs

        #Initialize output stream
        self._output = Output_Stream.output(self._debug_mode)
        self._output.play(self.getAudioBuffer)

        #Signal generation components
        self._amplitude = amplitude
        self._osc = osc.osc(wave_type)   #FIXME add parametric constructor support from midi CC

        #Voice handler
        self._voices = []
        for i in range(consts.MAX_VOICES):
            self._voices.append(UNUSED)

        #Signal processing components
        self._envelopes = []
        for i in range(consts.MAX_VOICES):
            self._envelopes.append(ADSR.ADSR())
        #self._filter = filter.filter() #FIXME implement

        #Mtof and Mton converters, just in case
        self._mtof = mtof.mtof()
        self._mton = mtof.mton()

    #Overloaded MIDI handler method, updates oscillator frequency, starts and stops playback
    def handleMessage(self, message):

        #Comment out to improve performance
        if self._debug_mode > 1:
            print("Synth MIDI Callback entered")

        #Update oscillator based on new frequency and trigger ADSR start
        #FIXME when ADSR exists, this is a hack
        if message.type == 'note_on' and self._mtof[message.note]:
            #Comment out to improve performance
            if self._debug_mode > 0:
                print(f"Note ON --- MIDI value: {message.note}, Velocity: {message.velocity}, Note: {mtof.mton_calc(message.note)}, Frequency: {mtof.mtof_calc(message.note)}")

            self.addVoice(message.note)
            if self._debug_mode > 0:
                print("Active voices:,", [x for x in self._voices if x != UNUSED])

            #FIXME trigger ADSR, calling the output directly is temporary! (Will require small
            #refactor. For example, passing the entire osc object seems wrong to me)
            self.addVoice(message.note)

            if not self._output._isPlaying:
                self._output._isPlaying = True

        #Trigger ADSR release
        #FIXME when ADSR exists, this is a hack
        elif message.type == 'note_off':
            if self._debug_mode > 0:
                print(f"Note OFF --- MIDI value: {message.note}, Velocity: {message.velocity}, Note: {mtof.mton_calc(message.note)}, Frequency: {mtof.mtof_calc(message.note)}")
            
            self.removeVoice(message.note)

            if self._debug_mode > 0:
                print("Active voices:,", [x for x in self._voices if x != UNUSED])

            #If no voices are active, stop playing
            active_voices = [v for v in self._voices if v != UNUSED]
            if not active_voices:
                self._output._isPlaying = False

        #FIXME outside of scope for now, but maybe worth looking into later
        #(map parameters to MIDI CC rather than a GUI...?)
        elif message.type == 'control_change':
            if self._debug_mode > 1:
                print(f"Control Change: {message.control}, Value: {message.value}")

    #Voice management
    def addVoice(self, new_voice: int = 0):
        #Only allow valid voices
        if new_voice < 21 or new_voice > 108:
            if self._debug_mode > 0:
                print("Invalid voice value, no new voice added")
            return
        
        #Find location for new voice, within voice limit. Repeat voices should retrigger their ADSR rather than add a new voice
        i = 0
        while self._voices[i] != UNUSED and i < consts.MAX_VOICES:
            if self._voices[i] == new_voice:
                self._envelopes[i].reset()
                if self._debug_mode > 0:
                    print("Redundant voice detected, resetting envelope")
                return
            i += 1
        if i >= consts.MAX_VOICES:
            if self._debug_mode > 0:
                print("Maximum voices exceeded, no new voice added")
            return

        #Update register, turn on envelope
        self._envelopes[i].on()
        self._voices[i] = new_voice
        return
    def removeVoice(self, old_voice: int = 0):
        
        #Only allow valid voices
        if old_voice < 21 or old_voice > 108:
            if self._debug_mode > 0:
                print("Invalid voice value, no voice removed")
            return
        
        #Find location for old voice, if it exists
        i = 0
        while self._voices[i] != old_voice and i < consts.MAX_VOICES:
            i += 1
        if i >= consts.MAX_VOICES:
            if self._debug_mode > 0:
                print("Voice was not active, no voice removed")
            return
        
        #Turn off envelope, mark voice as unused and reset envelope only if release stage has completed
        self._envelopes[i].off()
        self._envelopes[i].reset()
        self._voices[i] = UNUSED
        return

    #Consolidate audio from wavetable and voice list to a buffer for next step in signal chain
    def getAudioBuffer(self):
        #Start with silence
        mixed_buffer = np.zeros(consts.BUFFER_SIZE, np.int16)
        
        #Count active voices
        active_voices = [v for v in self._voices if v != UNUSED]
        num_active = len(active_voices)
        
        #Return silence if nothing active
        if num_active == 0:
            return mixed_buffer
        
        env_index = 0
        #Mix all active voices
        for voice in active_voices:
            #Get the oscillator data for this voice
            voice_data = self._osc[voice]

            #Fetch envelope data here
            voice_data = self._envelopes[env_index].applyEnvelope(voice_data)
            env_index += 1

            #Mix into the buffer (with scaling to prevent clipping)
            #Use float64 for the calculation to prevent overflow
            mixed_buffer = mixed_buffer.astype(np.float64) + (voice_data.astype(np.float64) / consts.MAX_VOICES)
        
        #Convert back to int16
        return mixed_buffer.astype(np.int16)
    
#Runs the synth
if __name__ == "__main__":
    synth = Synth(consts.WAVE_TYPE, consts.DEBUG_MODE)
    synth.printAllMIDIDevices()

    print("Connected to MIDI input:", synth._device_is_connected)

    #Visualize waveform or envelope FIXME how to show both?
    #synth._osc.drawWave()
    synth._envelopes[0].drawEnvelope()

    #Hack to let me test MIDI objects
    while True:
        time.sleep(1)
import numpy as np
import time
import mido

import MIDI_input as MIDI
import Output_Stream
import osc
import ADSR
import Waveform_Visualizer
import Filter

from lib import mtof
from lib import consts

UNUSED = -1


# FIXME commented out debug statements to check efficiency

#"Hub" class, defines signal flow up until Output_Stream
#   -IS A MIDI_device object
#   -HAS A(N) oscillator (osc)
#   -         envelope (ADSR)     see https://www.desmos.com/calculator/nrn6oabn6h for math
#   -         Filter (Filter)
#
class Synth(MIDI.MIDI_device):
    def __init__(self, wave_type: str = consts.WAVE_TYPE, debug_mode: int = consts.DEBUG_MODE, amplitude: float = 1.0, filter_type: str = consts.FILTER_TYPE, cutoff: int = consts.CUTOFF):
        
        super().__init__(consts.DEVICE_NAME)
        
        self._debug_mode = debug_mode #0 --- No debug outputs
                                      #1 --- Simple debug outputs
                                      #2 --- Verbose debug outputs

        #Signal generation components
        self._amplitude = amplitude
        self._osc = osc.osc(wave_type)   #FIXME add parametric constructor support from midi CC
        
        #Voice handler
        self._voices = []
        for i in range(consts.MAX_VOICES):
            self._voices.append(UNUSED)
        
        #Filter
        self._filter = Filter.Filter(cutoff, filter_type)

        #Envelope generator
        self._envelopes = []
        for e in range(consts.MAX_VOICES):
            self._envelopes.append(ADSR.ADSR(self._debug_mode))
            time.sleep(0.2)

        #Mtof and Mton converters, just in case
        self._mtof = mtof.mtof()
        self._mton = mtof.mton()
        
        #Visualizer class and output waveform list
        self._visualizer = Waveform_Visualizer.Plot()

        #Initialize output stream
        self._output = Output_Stream.output(self._debug_mode)
        self._output.play(self.getAudioBuffer)

    #Overloaded MIDI handler method, updates oscillator frequency, starts and stops playback
    def handleMessage(self, message):

        #Comment out to improve performance
        if self._debug_mode > 1:
            print("Synth MIDI Callback entered")

        #Update oscillator based on new frequency and trigger ADSR start
        #FIXME when ADSR exists, this is a hack
        if message.type == 'note_on' and self._mtof[message.note]:
            #if self._debug_mode > 0:
            #    print(f"\nNote ON --- MIDI value: {message.note}, Velocity: {message.velocity}, Note: {mtof.mton_calc(message.note)}, Frequency: {mtof.mtof_calc(message.note)}")

            self.addVoice(message.note)
            #if self._debug_mode > 0:
            #    print("Active voices:,", [x for x in self._voices if x != UNUSED])

            if not self._output._isPlaying:
                self._output._isPlaying = True

        #Trigger ADSR release
        #FIXME when ADSR exists, this is a hack
        elif message.type == 'note_off':
            #if self._debug_mode > 0:
            #    print(f"Note OFF --- MIDI value: {message.note}, Velocity: {message.velocity}, Note: {mtof.mton_calc(message.note)}, Frequency: {mtof.mtof_calc(message.note)}")
            
            self.releaseVoice(message.note)

            #if self._debug_mode > 0:
            #    print("Active voices:", [x for x in self._voices if x != UNUSED])

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
                self._envelopes[i].start()
                if self._debug_mode > 0:
                    print("Redundant voice detected, resetting envelope")
                return
            i += 1
        if i >= consts.MAX_VOICES:
            if self._debug_mode > 0:
                print("Maximum voices exceeded, no new voice added")
            return

        #Update register, turn on envelope
        self._envelopes[i].start()
        self._voices[i] = new_voice
        return
    def releaseVoice(self, rel_voice: int = 0):
        
        #Only allow valid voices
        if rel_voice < 21 or rel_voice > 108:
            if self._debug_mode > 0:
                print("Invalid voice value, no voice removed")
            return
        
        #Find location for old voice, if it exists
        i = 0
        while self._voices[i] != rel_voice and i < consts.MAX_VOICES - 1:
            i += 1
        if i >= consts.MAX_VOICES:
            if self._debug_mode > 0:
                print("Voice was not active, nothing to release")
            return
        
        if self._debug_mode > 1:
            print("Voice before release: ", self._voices[i])

        #Turn envelope to release phase
        self._envelopes[i].release()

        if self._debug_mode > 1:
            print("Voice after release: ", self._voices[i])
        return
    def pruneVoices(self):
        for i in range(consts.MAX_VOICES):
            if self._voices[i] != UNUSED and self._envelopes[i].isOff():
                self._voices[i] = UNUSED
                #if self._debug_mode > 1:
                #    print(f"Removing finished voice at index {i}")
            
    #Consolidate audio from wavetable and voice list to a buffer for next step in signal chain
    def getAudioBuffer(self):

        #For debugging efficiency, keep commented when not using
        #import time
        #start = time.perf_counter()
            
        #Ensure finished voices are set as such
        self.pruneVoices()

        #Start with silence
        mixed_buffer = np.zeros(consts.BUFFER_SIZE, np.float64)
    
        #Mix all active voices
        for i in range(len(self._voices)):
            if self._voices[i] != UNUSED:
                mixed_buffer += self._envelopes[i].applyEnvelope(self._osc[self._voices[i]]).astype(np.float64) / consts.MAX_VOICES
                
        #Apply filter
        filtered_buffer = self._filter.use(mixed_buffer)

        #if self._debug_mode > 0:
        #    ms = (time.perf_counter() - start)*1000
        #    if ms > 2:
        #        print(f"SLOW BUFFER GENERATION: {ms:.2f}ms")

        #Convert to int16
        return filtered_buffer.astype(np.int16)
    
    #Visualizes waveform and envelope
    def visualize(self) -> None:
        self._osc.drawWaveform(self._visualizer, 0)
        self._envelopes[0].drawEnvelope(self._visualizer, 1)
        self._visualizer.display()


#Runs the synth
if __name__ == "__main__":
    synth = Synth()
    synth.printAllMIDIDevices()

    print("Connected to MIDI input:", synth._device_is_connected)

    #Visualize wave and envelope data
    synth.visualize()

    #Either play the MIDI instrument or spoof some messages
    match synth._device_is_connected:
        case True:
            #Hack to let me test MIDI objects
            while True:
                time.sleep(1)
        case False:
            #Spoof a few notes
            for i in range(consts.MAX_VOICES * 2):
                synth.handleMessage(mido.Message('note_on', note=(consts.A_440 - (2 * consts.OCTAVE)) + (2 * i)))
                time.sleep(0.2)
                synth.handleMessage(mido.Message('note_off', note=(consts.A_440 - (2 * consts.OCTAVE)) + (2 * i)))
                time.sleep(0.2)
            time.sleep(consts.RELEASE + 0.2)
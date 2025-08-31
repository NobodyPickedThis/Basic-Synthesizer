import numpy as np
import time
import mido
import copy

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
        
        start = time.perf_counter()


        super().__init__(consts.DEVICE_NAME)
        
        self._debug_mode = debug_mode #0 --- No debug outputs
                                      #1 --- Simple debug outputs
                                      #2 --- Verbose debug outputs
                                      #3 --- Efficiency debug outputs

        if self._debug_mode == 3:
            base_class_timer = time.perf_counter() - start

        #Signal generation components
        self._amplitude = amplitude
        self._osc = osc.osc(wave_type)   #FIXME add parametric constructor support from midi CC

        if self._debug_mode == 3:
            osc_gen_timer = time.perf_counter() - start
        
        #Voice handler
        self._voices = []
        for i in range(consts.MAX_VOICES):
            self._voices.append(UNUSED)
        
        #Filter
        self._filter = Filter.Filter(cutoff, filter_type)

        if self._debug_mode == 3:
            filter_timer = time.perf_counter() - start

        #Envelope generator
        self._envelopes = []
        envelope = ADSR.ADSR(self._debug_mode)
        for e in range(consts.MAX_VOICES):
            self._envelopes.append(copy.deepcopy(envelope))

        if self._debug_mode == 3:
            env_timer = time.perf_counter() - start

        #Mtof and Mton converters, just in case
        self._mtof = mtof.mtof()
        self._mton = mtof.mton()

        if self._debug_mode == 3:
            midi_conv_timer = time.perf_counter() - start
        
        #Visualizer class and output waveform list
        self._visualizer = Waveform_Visualizer.Plot()

        if self._debug_mode == 3:
            vis_timer = time.perf_counter() - start

        #Initialize output stream
        self._output = Output_Stream.output(self._debug_mode)
        #Only use debug buffer provider if debug enabled
        if self._debug_mode == 3:
            self._output.play(self.getDebugAudioBuffer)
        else:
            self._output.play(self.getAudioBuffer)

        if self._debug_mode == 3:
            out_stream_timer = time.perf_counter() - start
            print()
            print(f"====================BOOTUP=INFO====================")
            print()
            print(f"\tBase Class initialized in: {(1000 * base_class_timer):.2f}ms")
            print(f"\tOscillator bank populated in: {(1000 * (osc_gen_timer - base_class_timer)):.2f}ms")
            print(f"\tFilter initialized in: {(1000 * (filter_timer - osc_gen_timer)):.2f}ms")
            print(f"\tEnvelopes initialized in: {(1000 * (env_timer - filter_timer)):.2f}ms")
            print(f"\tMIDI converters initialized in: {(1000 * (midi_conv_timer - env_timer)):.2f}ms")
            print(f"\tVisualizer initialized in: {(1000 * (vis_timer - midi_conv_timer)):.2f}ms")
            print(f"\tOutput stream initialized in: {(1000 * (out_stream_timer - vis_timer)):.2f}ms")
            print()
            print(f"TOTAL INTERNAL BOOT TIME: {(1000 * out_stream_timer):.2f}ms ({(out_stream_timer):.2f}s)")
            print(f"===================================================")

    #Overloaded MIDI handler method, updates oscillator frequency, starts and stops playback
    def handleMessage(self, message):

        #Comment out to improve performance
        if self._debug_mode == 2:
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
            if self._debug_mode == 2:
                print(f"Control Change: {message.control}, Value: {message.value}")

    #Voice management
    def addVoice(self, new_voice: int = 0):
        #Only allow valid voices
        if new_voice < 21 or new_voice > 108:
            if self._debug_mode > 0:
                print("Invalid voice value, no new voice added")
            return
        
        # Count active voices for debugging
        active_count = sum(1 for v in self._voices if v != UNUSED)
        
        # First check for duplicate voices:
        for i in range(consts.MAX_VOICES):
            if self._voices[i] == new_voice:
                self._envelopes[i].reset()
                self._envelopes[i].start()
                if self._debug_mode == 2:
                    print(f"Retriggering voice {new_voice} at index {i}")
                return

        # Next find UNUSED voices
        for i in range(consts.MAX_VOICES):
            if self._voices[i] == UNUSED:
                self._envelopes[i].start()
                self._voices[i] = new_voice
                return
            
        # If no duplicate or UNUSED voices, then find the oldest released voice
        oldest = 0
        for i in range(1, consts.MAX_VOICES):
            if self._envelopes[i].isOff() and not self._envelopes[oldest].isOff():
                oldest = i
        if self._envelopes[oldest].isOff():
            self._voices[oldest] = new_voice
            self._envelopes[oldest].reset()
            self._envelopes[oldest].start()
            if self._debug_mode == 0 or self._debug_mode == 2:
                print(f"Replaced oldest unused voice at index {oldest}")
            return
        
        # If all voices are busy, then replace the quietest one with the new note
        quietest = 0
        for i in range(1, consts.MAX_VOICES):
            if self._envelopes[i]._value < self._envelopes[quietest]._value:
                quietest = i
        self._voices[quietest] = new_voice
        self._envelopes[quietest].reset()
        self._envelopes[quietest].start()
        if self._debug_mode == 0 or self._debug_mode == 2:
            print(f"Stole voice from index {quietest}")
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
        
        if self._debug_mode == 2:
            print("Voice before release: ", self._voices[i])

        #Turn envelope to release phase
        self._envelopes[i].release()

        if self._debug_mode == 2:
            print("Voice after release: ", self._voices[i])
        return
    def pruneVoices(self):
        for i in range(consts.MAX_VOICES):
            if self._voices[i] != UNUSED and self._envelopes[i].isOff():
                self._voices[i] = UNUSED
                #if self._debug_mode == 2:
                #    print(f"Removing finished voice at index {i}")
            
    #Consolidate audio from wavetable and voice list to a buffer for next step in signal chain
    def getAudioBuffer(self):
            
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

        #Convert to int16
        return filtered_buffer.astype(np.int16)
    def getDebugAudioBuffer(self):

        start = time.perf_counter()
            
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

        ms = (time.perf_counter() - start)*1000
        if ms > 2:
            print(f"SLOW BUFFER GENERATION: {ms:.2f}ms")

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
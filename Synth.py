import numpy as np

import MIDI_input as MIDI
import Output_Stream
import osc
#import ADSR
#import filter

from lib import mtof
from lib import consts


#"Hub" class, defines signal flow up until Output_Stream
#   -IS A MIDI_device object
#   -HAS A(N) oscillator (osc)
#   -         envelope (ADSR)
#   -         Filter (Filter)
#
class Synth(MIDI.MIDI_device):
    def __init__(self, wave_type: str = "Sine", debug_mode: int = 0, amplitude: float = 1.0):
        
        super().__init__(consts.DEVICE_NAME)
        
        self._debug_mode = debug_mode #0 --- No debug outputs
                                      #1 --- Simple debug outputs
                                      #2 --- Verbose debug outputs
        if self._debug_mode > 0:
            print("IN DEBUG MODE:", self._debug_mode)

        #Initialize output stream
        self._output = Output_Stream.output(self._debug_mode)

        #========Signal generation and processing components========
        self._amplitude = amplitude
        self._soundbank = osc.osc(wave_type)                        #Wave data for all frequencies

        self._active_voices = []                                    #Notes (as MIDI) currently being played
        self._silence = np.zeros(consts.BUFFER_SIZE, float)
        self._current_output_data = self._silence

        #self._envelope = ADSR.ADSR()
        #self._filter = filter.filter() #FIXME implement

        #Mtof and Mton converters, just in case
        self._mtof = mtof.mtof()
        self._mton = mtof.mton()

    #Display first 10 samples of each frequency in the soundbank
    def printSoundBank(self):
        for i in range(21, 109):
            print(self._mton[i], ": [", self._soundbank[i][:10], " ...]", sep="")

    #Overloaded MIDI handler method, updates oscillator frequency, starts and stops playback
    def handleMessage(self, message):

        #Comment out to improve performance
        #if self._debug_mode > 0:
        #    print("Synth MIDI Callback entered")

        #Update oscillator based on new frequency and trigger ADSR start
        #FIXME when ADSR exists, this is a hack
        if message.type == 'note_on' and self._mtof[message.note]:
            #Comment out to improve performance
            if self._debug_mode > 0:
                print(f"Note ON --- MIDI value: {message.note}, Velocity: {message.velocity}, Note: {mtof.mton_calc(message.note)}, Frequency: {mtof.mtof_calc(message.note)}")

            #FIXME trigger ADSR, calling the output directly is temporary! (Will require small
            #refactor. For example, passing the entire osc object seems wrong to me)
            self.addVoice(message.note)

            #Comment out to improve performance
            if self._debug_mode > 1:
                print("Current Voices: ", self._active_voices, " Current output data (0-10):", self._current_output_data[:9]);

            self._output.play(self._current_output_data)

        #Trigger ADSR release
        #FIXME when ADSR exists, this is a hack
        elif message.type == 'note_off':
            
            #Comment out to improve performance
            if self._debug_mode > 0:
                print(f"Note OFF --- MIDI value: {message.note}, Velocity: {message.velocity}, Note: {mtof.mton_calc(message.note)}, Frequency: {mtof.mtof_calc(message.note)}")

            #FIXME trigger ADSR, calling the output directly is temporary! (Will require small
            #refactor. For example, passing the entire osc object seems wrong to me)
            self.removeVoice(message.note)

            #Comment out to improve performance
            if self._debug_mode > 1:
                print("Current Voices: ", self._active_voices, " Current output data (0-10):", self._current_output_data[:9]);

            self._output.play(self._current_output_data)


        #FIXME outside of scope for now, but maybe worth looking into later
        #(map parameters to MIDI CC rather than a GUI...?)
        elif message.type == 'control_change':
            if self._debug_mode > 1:
                print(f"Control Change: {message.control}, Value: {message.value}")
  
    #Adds a new voice to the active voices unless over cap
    def addVoice(self, new_voice: int = 0):

        #Comment out to improve performance
        #if self._debug_mode > 1:
        #    print("Entered addVoice")

        #Return if impossible
        if len(self._active_voices) > consts.MAX_VOICES:
            return
        
        #FIXME NOTHING HERE IS WORKING AAAAAA
        #Scale the new and old data by amounts proportional to the number total active voices, then merge
        new_data = np.multiply(np.array(self._soundbank[new_voice]), (1 / (1 + len(self._active_voices))))
        self._current_output_data = np.multiply(self._current_output_data, (1 - (1 / (1 + len(self._active_voices)))))
        self._current_output_data = np.add(self._current_output_data, new_data)
        
        #Update voice registry
        self._active_voices.append(new_voice)
    
    #Removes a voice from the active voices unless no voices currently exist
    def removeVoice(self, old_voice: int = 0):
        
        #Comment out to improve performance
        #if self._debug_mode > 1:
        #    print("Entered removeVoice")

        #Return if impossible
        if not self._active_voices:
            return
        
        elif len(self._active_voices) == 1:
            self._active_voices = []
            self._current_output_data = self._silence
            return
        
        #FIXME NOTHING HERE IS WORKING AAAAAA
        #Scale the data to remove by an amount proportional to the number of total voices
        #remove it, then scale old data back up
        remove_data = np.multiply(np.array(self._soundbank[old_voice]), (1 / (len(self._active_voices))))
        self._current_output_data = np.subtract(self._current_output_data, remove_data)
        self._current_output_data = np.add(self._current_output_data, (np.multiply(self._current_output_data, (1 / len(self._active_voices)))))

        #Update voice registry
        self._active_voices.remove(old_voice)

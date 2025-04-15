#External libraries
import numpy as np

#Other objects from this project
import MIDI_input as MIDI
import Output_Stream
import osc
#import ADSR
#import filter

#Utilities
from lib import mtof
from lib import consts

#Flag for indicating whether a given voice is off
UNUSED = -1

#"Hub" class, defines signal flow up until Output_Stream
#   -IS A MIDI_device object
#   -HAS A(N) Soundbank defined by an oscillator (osc)
#   -         Envelope (ADSR)
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
        self._amplitude = amplitude                                  #Master volume
        self._soundbank = osc.osc(wave_type)                         #Wave data for all frequencies

        self._silence = np.zeros(consts.BUFFER_SIZE, float)          #Silent output when a voice isn't active
        self._voices = [UNUSED for _ in range(consts.MAX_VOICES)]    #All currently active voices

        #self._envelope = ADSR.ADSR()   #FIXME implement, possibly in other file/class
        #self._filter = filter.filter() #FIXME implement, possibly in other file/class

        #Mtof and Mton converters, just in case
        self._mtof = mtof.mtof()
        self._mton = mtof.mton()

    #Display first 10 samples of each frequency in the soundbank
    def printSoundBank(self):
        for i in range(21, 109):
            print(self._mton[i], ": [", self._soundbank[i][:10], " ...]", sep="")
    #Display first 10 samples of each active voice
    def printActiveVoices(self):
        for x in self._voices:
            if x != UNUSED:
                print(self._mton[x], ": [", self._soundbank[x].data[:10], " ...]", sep="")
            else:
                print("Voice is unused")
    #Display first 10 samples of the flattened data
    def printFlattenedData(self, data):
        print("FLATTENED DATA: [", data[:10], " ...]", sep="")

    #Overloaded MIDI handler method, updates oscillator frequency, starts and stops playback
    def handleMessage(self, message):

        #Comment out to improve performance
        if self._debug_mode > 0:
            print("Synth MIDI Callback entered")

        #Update oscillator based on new frequency and trigger ADSR start
        #FIXME when ADSR exists, this is a hack
        if message.type == 'note_on' and self._mtof[message.note]:

            #FIXME trigger ADSR, calling the output directly is temporary! (Will require small
            #refactor. For example, passing the entire osc object seems wrong to me)
            self.addVoice(message.note)
            self._output.play(self.flattenVoices())

        #Trigger ADSR release
        #FIXME when ADSR exists, this is a hack
        elif message.type == 'note_off':
            #FIXME trigger ADSR, calling the output directly is temporary! (Will require small
            #refactor. For example, passing the entire osc object seems wrong to me)
            self.removeVoice(message.note)
            self._output.play(self.flattenVoices())

        #FIXME outside of scope for now, but maybe worth looking into later
        #(map parameters to MIDI CC rather than a GUI...?)
        elif message.type == 'control_change':
            if self._debug_mode > 1:
                print(f"Control Change: {message.control}, Value: {message.value}")
  
    #Adds a new voice to the active voices unless over cap
    def addVoice(self, new_voice: int = 0):

        #Comment out to improve performance
        if self._debug_mode > 0:
            print("Entered addVoice")

        #Find next unused voice
        new_voice_pos = UNUSED
        i = 0
        while i < consts.MAX_VOICES and new_voice_pos == UNUSED:
            if self._voices[i] == UNUSED:
                new_voice_pos = i
            else:
                i += 1

        #Return if impossible
        if i >= consts.MAX_VOICES or new_voice_pos == UNUSED:
            #Comment out to improve performance
            if self._debug_mode > 0:
                print("No more voices may be added!")
            return

        #Flag first unused voice as used by labelling it with which note it 
        #is playing (useful for removing that voice later!)
        self._voices[new_voice_pos] = new_voice     

        #Comment out to improve performance
        if self._debug_mode > 1:
            self.printActiveVoices()
             
    #Removes a voice from the active voices unless no voices currently exist
    def removeVoice(self, old_voice: int = 0):

        #Comment out to improve performance
        if self._debug_mode > 0:
            print("Entered removeVoice")

        #Find voice to be silenced
        old_voice_pos = -1
        for i in range(consts.MAX_VOICES):
            if self._voices[i] == old_voice:
                old_voice_pos = i
                break

        #Return if impossible
        if old_voice_pos == UNUSED:
            return
        
        #Flag voice as unused
        self._voices[old_voice_pos] = UNUSED     

        #Comment out to improve performance
        if self._debug_mode > 1:
            self.printActiveVoices()

    #Bundles data of all active voices to be sent to next stage in signal flow
    def flattenVoices(self) -> np.array:

        #Return and calculation variables
        summed_data = np.zeros(consts.BUFFER_SIZE, dtype=float)
        active_voices = [x for x in self._voices if x != UNUSED]
        num_voices = len(active_voices)

        #Comment out to improve performance
        if self._debug_mode > 0:
            print("Active voices:", num_voices)
        
        #Exit early if needed
        if num_voices == 0:
            return (self._silence * 32767).astype(np.int16)

        #Sum all voices
        for x in self._voices:
            if x != UNUSED:
                summed_data = np.add(summed_data, self._soundbank[x])

        #Avoid div by 0
        if num_voices > 1:
            #Renormalize by scaling the sum down proportionally to the number of active voices
            renormalized_data = np.divide(summed_data, np.full(consts.BUFFER_SIZE, fill_value=num_voices, dtype=float))
        else:
            #Single voice or silence
            renormalized_data = summed_data

        #Clip to [-1, 1]
        clipped_data = np.clip(renormalized_data, -1.0, 1.0)
        
        #Convert to 16-bit audio
        int16_data = (clipped_data * 32767).astype(np.int16)    #Offset so that first sample is 0 FIXME hopefully this offset is still accurate after moving this from osc...?
        
        #Comment out to improve performance
        if self._debug_mode > 0:
            self.printFlattenedData(int16_data)
        
        return int16_data
import MIDI_input as MIDI
import Output_Stream
import osc
#import ADSR
#import filter
import consts

DEVICE_NAME = 'MPKmini2'



#"Hub" class, defines signal flow up until Output_Stream
#   -IS A MIDI_device object
#   -HAS A(N) oscillator (osc)
#   -         envelope (ADSR)
#   -         Filter (Filter)
#
class Synth(MIDI.MIDI_device):
    def __init__(self, debug_mode: int = 0, amplitude: float = 1.0):
        
        super().__init__(DEVICE_NAME)
        
        self._debug_mode = debug_mode #0 --- No debug outputs
                                      #1 --- Simple debug outputs
                                      #2 --- Verbose debug outputs

        #Initialize output stream
        self._output = Output_Stream.output()

        #Connect to device
        self._MIDI_device = MIDI.MIDI_device(DEVICE_NAME)

        #Signal generation and processing components
        self._amplitude = amplitude
        self._osc = osc.osc()   #FIXME add parametric constructor support
        #self._envelope = ADSR.ADSR()
        #self._filter = filter.filter() #FIXME implement


    #Overloaded processMIDI method, updates oscillator frequency, starts and stops playback
    def processMIDI(self, message = None):

        #Update oscillator based on new frequency and trigger ADSR start
        if message.type == 'note_on' and self._mtof[message.note]:
            self._osc.update_wave(message.note)

            #FIXME trigger ADSR, calling the output directly is temporary! (Will require small
            #refactor. For example, passing the entire osc object seems wrong to me)
            self._output.play(self._osc)

        #Trigger ADSR release
        #FIXME when ADSR exists
        elif message.type == 'note_off':
            if self._debug_mode > 1:
                print(f"Note OFF: {message.note}, Velocity: {message.velocity}")
            self._output.stop()

        #FIXME outside of scope for now, but maybe worth looking into later
        #(map parameters to MIDI CC rather than a GUI...?)
        elif message.type == 'control_change':
            if self._debug_mode > 1:
                print(f"Control Change: {message.control}, Value: {message.value}")

    
        

import pyaudio
import osc
from lib import consts
import numpy as np
from operator import add

#Handles stream open, write, and close functionality
class output:

    #Initialize pyaudio output stream
    def __init__(self, debug_mode: int = 0):
        self._p = pyaudio.PyAudio()     
        self._stream = None
        self._audio_data = None
        self._debug_mode = debug_mode #0 --- No debug outputs
                                      #1 --- Simple debug outputs
                                      #2 --- Verbose debug outputs

        self._silence = bytes(np.zeros(consts.BUFFER_SIZE, np.int16))
        self._MIDI_values = []
        
    #Don't leave the stream open!
    def __del__(self):
        if self._debug_mode > 0:
            print("Destroying output object")
        self.stop()
        self._p.terminate()

    #Write to output stream
    def play(self, wave_data, MIDI_value: int = 0):

        if MIDI_value > 0:
            self._MIDI_values.append(MIDI_value)
        elif MIDI_value < 0:
            self._MIDI_values.remove(abs(MIDI_value))

        # Define callback function that PyAudio will call when it needs more audio data
        def callback(in_data, frame_count, time_info, status):
            
            #If no notes should play (or flag is off) set to silence
            if not wave_data or not self._MIDI_values:
                return(self._silence, pyaudio.paContinue)
                
            #Sum all active notes
            voices = len(self._MIDI_values)
            new_data = np.zeros(consts.BUFFER_SIZE)
            for i in range(voices):
                new_data = np.array(list(map(add, new_data, wave_data[self._MIDI_values[i]])))
            #Normalize
            new_data = ((new_data - np.min(new_data)) / (np.max(new_data) - np.min(new_data))) * 256

            #FIXME debugging polyphony algorithm
            if self._debug_mode > 1:
                print(max(new_data), min(new_data))
                print(new_data[0:10])

            #Convert to bytes
            out_data = bytes(new_data)
            return (out_data, pyaudio.paContinue)

        #Open new stream (if no others are alreayd open) with callback
        if self._stream is None:
            self._stream = self._p.open(
                format=pyaudio.paInt16, 
                channels=1,
                rate=consts.BITRATE,
                output=True,
                stream_callback=callback,
                frames_per_buffer=consts.BUFFER_SIZE
            )
        
            #Start the stream
            self._stream.start_stream()

    #Close stream
    def stop(self):
        self._current_data = None
        if self._debug_mode > 0:
            print("Stopping stream")
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
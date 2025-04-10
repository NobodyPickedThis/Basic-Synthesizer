import pyaudio
import osc
from lib import consts
import numpy as np

#Handles stream open, write, and close functionality
class output:

    #Initialize pyaudio output stream
    def __init__(self, debug_mode: int = 0):
        self._p = pyaudio.PyAudio()     
        self._stream = None
        self._isPlaying = False
        self._audio_data = None
        self._debug_mode = debug_mode #0 --- No debug outputs
                                      #1 --- Simple debug outputs
                                      #2 --- Verbose debug outputs

        self._silence = np.zeros(consts.BUFFER_SIZE, np.int16)
        
    #Don't leave the stream open!
    def __del__(self):
        if self._debug_mode > 0:
            print("Destroying output object")
        self.stop()
        self._p.terminate()

    #Write to output stream
    def play(self, wave_bank: osc.osc = None, MIDI_value: int = 0):

        # Define callback function that PyAudio will call when it needs more audio data
        def callback(in_data, frame_count, time_info, status):
            
            #Assume data has been given
            new_data = wave_bank[self._current_MIDI]
            
            #If it hasn't (or flag is off) set to silence
            if not self._isPlaying or wave_bank is None:
                new_data = self._silence
                
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
        self._isPlaying = True
        self._current_MIDI = MIDI_value

    #Close stream
    def stop(self):
        self._current_data = None
        if self._debug_mode > 0:
            print("Stopping stream")
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        self._isPlaying = False

    def isPlaying(self) -> bool:
        # Also check if stream is active
        if self._stream is not None and not self._stream.is_active():
            self._isPlaying = False
        return self._isPlaying
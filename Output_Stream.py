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

        
    #Don't leave the stream open!
    def __del__(self):
        if self._debug_mode > 0:
            print("Destroying output object")
        self.stop()
        self._p.terminate()

    #Write to output stream
    def play(self, wave_data: np.array):

        #Store wave_data
        self._audio_data = wave_data

        # Define callback function that PyAudio will call when it needs more audio data
        def callback(in_data, frame_count, time_info, status):

            #FIXME remove when possible ;-;
            #print("Output audio data (10 samples):", self._audio_data[:10], sep="")
          
            out_data = bytes(self._audio_data)
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

    #Reset to silence
    def pause(self):
        self.play(np.zeros(consts.BUFFER_SIZE, np.int16))

    #Close stream
    def stop(self):
        self._audio_data = None
        if self._debug_mode > 0:
            print("Stopping stream")
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
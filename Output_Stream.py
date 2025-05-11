import pyaudio
from lib import consts
import numpy as np

#Handles stream open, write, and close functionality
class output:

    #Initialize pyaudio output stream
    def __init__(self, debug_mode: int = 0):
        self._p = pyaudio.PyAudio()     
        self._stream = None
        self._isPlaying = False
        self._buffer_provider = None
        self._debug_mode = debug_mode #0 --- No debug outputs
                                      #1 --- Simple debug outputs
                                      #2 --- Verbose debug outputs

        self._silence = np.zeros(consts.BUFFER_SIZE, np.int16)

        self.initStream(self._buffer_provider)
        
    #Don't leave the stream open!
    def __del__(self):
        if self._debug_mode > 0:
            print("Destroying output object")
        self.stop()
        self._p.terminate()

    #Initialize stream and callback
    def initStream(self, buffer_provider):
        self._buffer_provider = buffer_provider
        
        # Define the callback
        def stream_callback(in_data, frame_count, time_info, status):
            if not self._isPlaying or self._buffer_provider is None:
                return (self._silence.tobytes(), pyaudio.paContinue)
            
            # Get fresh data from the buffer provider
            new_data = self._buffer_provider()
            
            #if self._debug_mode > 1:
            #    print(f"Callback getting fresh data from provider")
            #    print(f"First few samples: {new_data[:5]}")
            
            return (new_data.tobytes(), pyaudio.paContinue)
        
        # Create the stream
        if self._stream is None:
            self._stream = self._p.open(
                format=pyaudio.paInt16, 
                channels=1,
                rate=consts.BITRATE,
                output=True,
                stream_callback=stream_callback,
                frames_per_buffer=consts.BUFFER_SIZE
            )
            self._stream.start_stream()
            self._isPlaying = True
        
    #Write to output stream using provided buffer
    def play(self, buffer_provider):

        self._buffer_provider = buffer_provider

        #Open new stream (if no others are already open) with callback
        if self._stream is None:
            self.initStream(buffer_provider)
        
        self._isPlaying = True

    #Close stream
    def stop(self):
        self._current_data = self._silence
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
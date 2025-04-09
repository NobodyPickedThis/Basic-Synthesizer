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
    def play(self, audio_data):

        # Define callback function that PyAudio will call when it needs more audio data
        def callback(in_data, frame_count, time_info, status):

            #Comment out for performance within callback
            #if self._debug_mode > 0:
            #    print("Output Stream Callback entered, requesting", frame_count, "frames")

            #Assume data has been given
            new_data = audio_data
            
            #If it hasn't (or flag is off) set to silence
            if not self._isPlaying or audio_data is None:
            #    Comment out for performance within callback
                #if self._debug_mode > 0:
                #    print("Callback exiting early:", end=" ")
                #    if not self._isPlaying:
                #        print("Stream is turned off!")
                #    else:
                #        print("No data provided!")
                new_data = self._silence
                
            #Convert to bytes
            out_data = bytes(new_data)
            #if self._debug_mode > 0:
            #    print("Callback complete")
            return (out_data, pyaudio.paContinue)

        #Making sure no other stream is open
        if self._stream is not None:
            self._stream.close()

        #Open new stream with callback
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

        #Comment out for performance
        #if self._debug_mode > 0:
        #    if self._isPlaying == False or self._stream.is_stopped() or not self._stream.is_active():
        #        print("Stream not successfully opened!")
        #        print("self._isPlaying is", self._isPlaying)
        #        print("self._stream.is_stopped() is", self._stream.is_stopped())
        #        print("self._stream.is_active()", self._stream.is_active())

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
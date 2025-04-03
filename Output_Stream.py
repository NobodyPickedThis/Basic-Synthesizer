import pyaudio
import osc
import consts

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
        
    #Don't leave the stream open!
    def __del__(self):
        if self._debug_mode > 0:
            print("Destroying output object")
        self.stop()
        self._p.terminate()

    #Write to output stream
    def play(self, oscillator: osc.osc):

        self._audio_data = oscillator

        # Define callback function that PyAudio will call when it needs more audio data
        def callback(in_data, frame_count, time_info, status):

            if self._debug_mode > 0:
                print("Callback entered, requesting", frame_count, "frames")
            
            if not self._isPlaying or self._audio_data is None:
                if self._debug_mode > 0:
                    print("Callback exiting early:", end=" ")
                    if not self._isPlaying:
                        print("Stream is turned off!")
                    else:
                        print("No oscillator provided!")
                self._isPlaying = False
                return (None, pyaudio.paComplete)

            #Else continue to play the samples, converting np.array to bytes
            new_data = self._audio_data.getWavedata(frame_count)
            out_data = bytes(new_data)
            if self._debug_mode > 0:
                print("Callback complete")
            return (out_data, pyaudio.paContinue)

        #Open new stream with callback
        self._stream = self._p.open(
            format=pyaudio.paInt8, 
            channels=1,
            rate=consts.BITRATE,
            output=True,
            stream_callback=callback,
            frames_per_buffer=consts.BUFFER_SIZE
        )
        
        #Start the stream
        self._stream.start_stream()
        self._isPlaying = True

        if self._debug_mode > 0:
            if self._isPlaying == False or self._stream.is_stopped() or not self._stream.is_active():
                print("Stream not successfully opened!")
                print("self._isPlaying is", self._isPlaying)
                print("self._stream.is_stopped() is", self._stream.is_stopped())
                print("self._stream.is_active()", self._stream.is_active())

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
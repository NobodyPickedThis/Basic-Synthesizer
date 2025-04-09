=====FEATURES TO WORK ON=====
 1) Realtime performance ideas to try:
    - Precalculate wavedata for all frequencies (2d np.array?), then only 
        change a "current frequency" value in Synth object
    - Less starting and stopping the stream, find a way to leave it open 
        but just send silence?
    - Create copies of functions with debug text so that I don't have to 
        comment/uncomment when trying to minimize latency/check debug 
        output, respectively.

 2) ADSR
    - Should take note_on / note_off triggers and convert to scalar multipliers
        to apply to wavedata in "some way(tm)"

 3) Polyphony
    - I'll figure it out

 4) Filter    
    - Should take midi CC value and pass all audio through before output but after
        ADSR, again in "some way(tm)"
=====FEATURES TO WORK ON=====
 1) ADSR
    - Should take note_on / note_off triggers and convert to scalar multipliers
        to apply to wavedata in "some way(tm)"

 2) Apply MIDI CC to Synth parameters
    - Should be able to change (or interpolate between!) wave types, adjust amplitude
    - Be scalable for when more features are added

 3) Filter    
    - Should take midi CC value and pass all audio through before output but after
        ADSR, again in "some way(tm)"
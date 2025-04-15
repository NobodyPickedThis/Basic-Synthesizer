=====FEATURES TO WORK ON=====
 1) Polyphony
    - I'll figure it out

 2) ADSR
    - Should take note_on / note_off triggers and convert to scalar multipliers
        to apply to wavedata in "some way(tm)"

 3) Apply MIDI CC to Synth parameters
    - Should be able to change (or interpolate between!) wave types, adjust amplitude
    - Be scalable for when more features are added

 4) Filter    
    - Should take midi CC value and pass all audio through before output but after
        ADSR, again in "some way(tm)"

 5) Interesting Synthesis
    - Implement some combination of additive, FM, etc...
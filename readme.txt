=====SETUP=====
 1) Set up a virtual environment in the working directory

 2) Install dependencies using pip (numpy, matplotlib, mido, pyaudio)

 3) Run Synth.py


=====FEATURES TO WORK ON=====
 1) Filter    
    - Should take midi CC value and pass all audio through before output but after
        ADSR, again in "some way(tm)"

 2) Apply MIDI CC to Synth parameters
    - Should be able to change (or interpolate between!) wave types, adjust amplitude
    - Be scalable for when more features are added



=====ISSUES=====

 1) Tone is still colored, most notable when using Sine.

 2) Filter is only 2-pole
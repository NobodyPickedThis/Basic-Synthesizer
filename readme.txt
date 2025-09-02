=====SETUP=====
 1) Set up a virtual environment in the working directory

 2) Install dependencies using pip (numpy, matplotlib, mido, pyaudio)

 3) Configure consts.py to recognize your hardware (although autodetection should hopefully handle outputs if set to '')

 4) Run Synth.py


=====FEATURES TO WORK ON=====

 1) Apply MIDI CC to Synth parameters
    - Should be able to change (or interpolate between!) wave types, adjust amplitude
    - Be scalable for when more features are added



=====ISSUES=====

 1) Tone is still colored, most notable when using Sine.

 2) Cutoff Modulation is choppy. Could probably use interpolation?
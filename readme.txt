=====SETUP=====
 1) Set up a virtual environment in the working directory

 2) Install dependencies using pip (numpy, matplotlib, mido, pyaudio)

 3) Run Synth.py


=====FEATURES TO WORK ON=====
 1) Apply MIDI CC to Synth parameters
    - Should be able to change (or interpolate between!) wave types, adjust amplitude
    - Be scalable for when more features are added

 2) Filter    
    - Should take midi CC value and pass all audio through before output but after
        ADSR, again in "some way(tm)"


=====ISSUES=====
 1) Decouple MAX_VOICES from gain by using a conversion factor to compensate
	for lower gain (of a single voice) using a higher voice limit. Basically,
	a single voice should be the same volume regardless of voice cap.

 2) Sometimes there's an index out of range issue on line 111 of Synth.py when
	near the voice limit. Implementing overriding of older voices should
	help get rid of this.

 3) Tone is still colored, most notable when using Sine.
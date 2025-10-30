# =============== SYNTH PARAMETERS ================

# Supports "Sine" "Saw" or "Square"
WAVE_TYPE = "Sine"           

# MIDI CC Bindings
ATTACK_CC = 1
DECAY_CC = 2
SUSTAIN_CC = 3
RELEASE_CC = 4
CUTOFF_CC = 5
Q_CC = 6
WAVE_CC = 7

FILTER_TYPE = "hi_cut"  # "hi_cut" or "low_cut"
FILTER_ON = True    
POLES = 2   # 2 or 4 
            # If you're having latency / underruns in 4, swapping to 2 could help

# =================================================









# ========== HARDWARE & DEBUG PARAMETERS ==========

# Name of desired device (or leave blank '' for auto detection) 
DEVICE_NAME = ''
INTERFACE_NAME = ''
AUDIO_API = ''

DEBUG_MODE = 0              #0 --- No debug outputs
                            #1 --- Simple debug outputs
                            #2 --- Verbose debug outputs
                            #3 --- Efficiency debug outputs (Does not include many other debug outputs)

# Debugging buffer efficiency threshold (ms)
TOO_SLOW = 2.0

BITRATE = 48000
BUFFER_SIZE = 256
MAX_VOICES = 8

# =================================================









# =============== REFERENCE VALUES ================
NYQUIST = BITRATE / 2

# MIDI control values
A_440 = 69
OCTAVE = 12
NOTE_ON = 1
NOTE_OFF = 0

# Envelope state tracking
OFF = 0
A = 1
D = 2
S = 3
R = 4

# Filter type values
LOW_CUT = "low_cut"
HI_CUT = "hi_cut"

# General frequency ranges (filter frequency range can be adjusted below)
MAX_FREQ = 20000
MIN_FREQ = 20
MAX_MIDI = 127

# Graph (Visualizer) properties
NUM_GRAPHS = 3
WAVEFORM_PLOT = 0
ADSR_PLOT = 1
FILTER_PLOT = 2

# Bounds for ADSR parameters
MAX_ATTACK  = 1.000
MIN_ATTACK  = 0.005
MAX_DECAY   = 1.500
MIN_DECAY   = 0.100
MAX_SUSTAIN = 1.000
MIN_SUSTAIN = 0.000
MAX_RELEASE = 3.000
MIN_RELEASE = 0.005

EXPONENTIAL_DECAY_COEFFICIENT = 3.000   # 0: linear release
                                        # 1: Standard exponential release
                                        # >1: More dramatic exponential release

# Filter parameters
MIN_FILTER_FREQ = 60
MAX_FILTER_FREQ = 20000
MAX_Q = 2
MIN_Q = 0.5
INTERP_STEPS = 4 # Precision of interpolation

# =================================================
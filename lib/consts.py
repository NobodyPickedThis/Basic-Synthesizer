 # ========== REFERENCE VALUES ==========
BITRATE = 44100
BUFFER_SIZE = 128

DEVICE_NAME = 'MPKmini2'

MAX_VOICES = 8
A_440 = 69
OCTAVE = 12

NOTE_ON = 1
NOTE_OFF = 0

# Envelope state tracking
OFF = 0
ADS = 1
R = 2

# Filter type values
LOW_CUT = "low_cut"
HI_CUT = "hi_cut"

# Frequency ranges
MAX_FREQ = 20000
MIN_FREQ = 0

NUM_GRAPHS = 2

DEBUG_MODE = 0              #0 --- No debug outputs
                            #1 --- Simple debug outputs
                            #2 --- Verbose debug outputs





# ========== TUNABLE PARAMETERS ==========

# Supports "Sine" "Saw" or "Square"
WAVE_TYPE = "Saw"           

ATTACK =  0.350             # in s
DECAY =   1.000             # in s
SUSTAIN = 1.000
RELEASE = 1.350             # in s

# Hz, 0 - 20000
CUTOFF = 2000    
FILTER_TYPE = LOW_CUT   
FILTER_ON = True       
BITRATE = 44100
BUFFER_SIZE = 128

DEVICE_NAME = 'MPKmini2'

MAX_VOICES = 8
MIDDLE_C = 69

WAVE_TYPE = "Saw"           #Supports "Sine" "Saw" or "Square"

ATTACK =  0.350             #in s
DECAY =   1.000             #in s
SUSTAIN = 1.000
RELEASE = 1.350             #in s

NOTE_ON = 1
NOTE_OFF = 0

#Envelope state tracking
OFF = 0
ADS = 1
R = 2

NUM_GRAPHS = 2

DEBUG_MODE = 0              #0 --- No debug outputs
                            #1 --- Simple debug outputs
                            #2 --- Verbose debug outputs
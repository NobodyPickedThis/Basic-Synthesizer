import matplotlib.pyplot as plt
import numpy as np
import consts
#import wave, sys

def drawWaveform(WAVEFORM: list) -> None:
    
    plt.close()
    plt.plot(WAVEFORM)
    plt.ion()
    plt.show()
    plt.pause(0.001)


import matplotlib.pyplot as plt

def drawWaveform(WAVEFORM: list) -> None:
    
    plt.close()
    plt.plot(WAVEFORM)
    plt.ion()
    plt.show()
    plt.pause(0.001)
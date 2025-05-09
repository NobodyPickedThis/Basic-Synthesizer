import matplotlib.pyplot as plt
from lib import consts


class Plot():
    def __init__(self, a1: int = consts.NUM_GRAPHS) -> None:
        plt.close()
        plt.ion()
        self._figure, self._axis = plt.subplots(a1)

    def __del__(self):
        plt.close

    def display(self):
        plt.show()
        plt.pause(0.001)

    def drawWaveform(self, waveform: list, pos: int = 0) -> None:
        self._axis[pos].plot(waveform)
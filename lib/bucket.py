import numpy as np

class bucket():
    def __init__(self):
        self._bucket = []
        f = open("bucket.txt", "r")
        count = 0
        for line in f:
            self._bucket.extend(format(count, line.strip()))
            count += 1
        line.strip()
        f.close()

    # Visualize bucket
    def drawBucket(self, plot, pos: int = 1) -> None:
        plot.drawWaveform(self._bucket, pos)
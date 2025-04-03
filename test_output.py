import Output_Stream
import osc
import time
import numpy as np
import consts

test_osc = osc.osc(440)

#Arg indicates debug mode: 0 = off, 1 = simple, 2 = verbose
test_out = Output_Stream.output(0)

test_out.play(test_osc)
time.sleep(1)
test_out.stop()
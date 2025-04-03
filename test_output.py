import Output
import osc
import time
import numpy as np

test_osc = osc.osc()

#Arg indicates debug mode: 0 = off, 1 = simple, 2 = verbose
test_out = Output.output(2)

test_out.play(test_osc.getWavedata())
time.sleep(1)
test_out.stop()

#FIXME is this white noise??
#test_out.play([1])
#time.sleep(2)
#test_out.stop()
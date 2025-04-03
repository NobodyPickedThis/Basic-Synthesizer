import Output_Stream
import osc
import time
import numpy as np
import consts

#Generate and draw waves
sine_osc = osc.osc(440, "Sine")
square_osc = osc.osc(440, "Square")
saw_osc = osc.osc(440, "Saw")
sine_osc.draw_wave()
time.sleep(1)
square_osc.draw_wave()
time.sleep(1)
saw_osc.draw_wave()
time.sleep(1)

#Arg indicates debug mode: 0 = off, 1 = simple, 2 = verbose
test_out = Output_Stream.output(0)

#Play waves
test_out.play(sine_osc)
time.sleep(1)
test_out.stop()
time.sleep(0.5)

test_out.play(sine_osc)
time.sleep(1)
test_out.stop()
time.sleep(0.5)

test_out.play(sine_osc)
time.sleep(1)
test_out.stop()
time.sleep(0.5)
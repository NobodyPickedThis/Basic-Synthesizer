import Output_Stream
import osc
import time
import numpy as np
import consts

#Arg indicates debug mode: 0 = off, 1 = simple, 2 = verbose
test_out = Output_Stream.output(0)

#SINE
sine_osc = osc.osc(200, "Sine")
sine_osc.draw_wave()
time.sleep(1)
test_out.play(sine_osc)
time.sleep(1)
test_out.stop()
time.sleep(0.5)

#SQUARE
square_osc = osc.osc(200, "Square")
square_osc.draw_wave()
time.sleep(1)
test_out.play(square_osc)
time.sleep(1)
test_out.stop()
time.sleep(0.5)

#SAW
saw_osc = osc.osc(440, "Saw")
saw_osc.draw_wave()
time.sleep(1)
test_out.play(saw_osc)
time.sleep(1)
test_out.stop()
time.sleep(0.5)
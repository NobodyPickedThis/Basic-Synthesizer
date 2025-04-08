import Output_Stream
import osc
import time
import numpy as np

#Arg indicates debug mode: 0 = off, 1 = simple, 2 = verbose
test_out = Output_Stream.output(0)

#SINE
def test_sine(test_out: Output_Stream.output):
    sine_osc = osc.osc(200, "Sine")
    if test_out._debug_mode > 1:
        sine_osc.print_wave()
    sine_osc.draw_wave()
    time.sleep(1)
    test_out.play(sine_osc)
    time.sleep(1)
    test_out.stop()
    time.sleep(0.5)

#SQUARE
def test_square(test_out: Output_Stream.output):
    square_osc = osc.osc(200, "Square")
    if test_out._debug_mode > 1:
        square_osc.print_wave()
    square_osc.draw_wave()
    time.sleep(1)
    test_out.play(square_osc)
    time.sleep(1)
    test_out.stop()
    time.sleep(0.5)

#SAW
def test_saw(test_out: Output_Stream.output):
    saw_osc = osc.osc(200, "Saw")
    if test_out._debug_mode > 1:
        saw_osc.print_wave()
    saw_osc.draw_wave()
    time.sleep(1)
    test_out.play(saw_osc)
    time.sleep(1)
    test_out.stop()
    time.sleep(0.5)

#===========TEST CALLS===========
#test_sine(test_out)
#test_square(test_out)
#test_saw(test_out)
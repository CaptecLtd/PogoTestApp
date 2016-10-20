"""
FunctionTests

Script to test functionality of the pogolib.input module without running through the application
"""

from PogoTestApp.pogolib.adc import Channel

channels = []

for val in range(0, 8):
    channels.append(Channel(val +1))

for ch in channels:
    print("Channel %s reports %dv" % (ch.index, ch.read_voltage()))

print("Please supply +5v to channel 1. Press Enter when complete")
input()

ch1_voltage = channels[0].read_voltage()

if ch1_voltage == 5.0:
    print("+5v read on channel one, continuing")
else:
    print("Read voltage (%d) was not +5v" % ch1_voltage)
    exit

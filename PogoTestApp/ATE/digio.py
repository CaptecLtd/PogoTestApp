"Digital I/O abstraction module"

try:
    import RPi.GPIO as GPIOBase
except RuntimeError:
    print("GPIO libraries could not be loaded. NO HARDWARE INTERACTION WILL TAKE PLACE.")


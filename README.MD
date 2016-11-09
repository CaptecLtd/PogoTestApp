# PogoTestApp
## Purpose
This is a software control application for an ATE (Automatic Test Equipment) unit. The application is written in Python 3.

### Run the application
Execute PogoTestApp.py with `python PogoTestApp.py`. Use the `-f` argument to make the GUI full screen.

### Unit tests
Run some basic unit tests with `python UnitTests.py`.

## Platform
The application is part of a greater project for my employer, an ATE for testing power and battery PCBs. The project uses a Raspberry Pi 3 as the ATE controller with a touch screen for the user interface.

## pogolib Modules
### adc.py
Provides interaction with an analogue to digital converter board for reading voltages. Currently supports the ADCPi Plus from AB Electronics but could be abstracted to another type of device.

Each analogue channel is represented by a `Channel` class. Pass the channel number as the constructor.

Channels can be put in simulation mode by calling `set_simulation_mode(True)` on the channel after constructing it.

Simulation mode returns whatever is set by `set_simulation_voltage()`. This is used for unit testing the ADC module's functions.

### gui.py
Handles GUI interaction and events. Python's TKinter is used as the GUI framework.

### suite.py
Provides an interface between the GUI and the tests being run. Each instance of TestProcedure is added to the current test suite, with tests advancing on a pass or fail.

### tests.py
The main module for tests. Each class is an instance of TestProcedure and should implement the method `run()`. The class can optionally implement the `setUp()` and `tearDown()` methods which are run before and after tests respectively.
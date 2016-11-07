# Constants required by the specification are declared here.

# Header for initial startup.
INTRO_TEXT = """Captec X231 PCBA Rev: {hwrevision} Test System
Copyright 2016 Captec Ltd.
ATE Software Ver: {swrevision}  - {swdate} 

Press RESET to begin."""

# These reference analogue channels on the ADC.
AD1_Pogo_Input_Volts = 1
AD2_Tablet_USB_Volts = 2
AD3_Batt_Board_Power_In_Volts = 3
AD4_Batt_Board_Temp_Sense_Cutoff = 4
AD5_Batt_Board_Battery_Volts = 5
AD6_External_USB_Volts = 6
AD7_Pogo_Battery_Output = 7

# Digital Inputs
# These correspond to the GPIO pins (BCM naming convention)
DIP1_TP3_Q4_Startup_Delay = 0
DIP2_Tablet_OTG_Sense = 0
DIP3_Dplus_Tablet_USB_Sense = 0
DIP4_Dminus_Tablet_USB_Sense = 0

# Digital Outputs
# These correspond to the GPIO pins (BCM naming convention)
DOP1_Tablet_Full_Load_Switch = 0
DOP2_Tablet_Changed_Load_Switch = 0
DOP3_OTG_Mode_Trigger = 0
# Constants required by the specification are declared here.

# Header for initial startup.
INTRO_TEXT = """Captec X230/X232 PCBA Rev: {hwrevision} Test System
Copyright 2016-2019 Captec Ltd.
ATE Software Ver: {swrevision} - {swdate} 

Ensure the PCBA jigs are UNPOPULATED. All switches must be in OFF position. Power supply must be ON.

Press MENU, RESET to begin testing."""


# Pin assignments

# These reference analogue channels on the ADC.
AD1_V_pogo = 1
AD2_V_5V_pwr = 2
AD3_V_in = 3
AD4_V_TP13_NTC = 4
AD5_V_bat = 5
AD6_V_sense = 6
AD7_V_sys_out = 7
AD8_V_out = 8

# Digital Inputs
# These correspond to the GPIO pins (BCM naming convention)
DIP1_PWRUP_Delay = 23
DIP2_OTG_OK = 27
DIP3_Dplus_J5_3_OK = 26
DIP4_Dminus_J5_2_OK = 19
DIP5_5V_PWR = 22
DIP6_From_J7_4 = 6
DIP7_J3_LINK_OK = 20
DIP8_LED_RD = 16
DIP9_LED_GN = 12
DIP10_USB_PERpins_OK = 8
DIP11_5V_ATE_in = 24

# Digital Outputs
# These correspond to the GPIO pins (BCM naming convention)
DOP1_Load_ON = 17
DOP2_Discharge_Load = 10
DOP3_TP7_GPIO = 25
DOP4_TP5_GPIO = 4
DOP5_TP6_GPIO = 21
DOP6_T_SW_ON = 18
DOP7_Cold_sim = 9
DOP8_Hot_sim = 11
DOP9_TO_J7_1 = 5
DOP10_FLT_loop_back = 13
DOP11_POGO_ON_GPIO = 7
DOP12_BAT1_GPIO = 15
DOP13_BAT0_GPIO = 14
import os
import re
import shutil
import ensight
import numpy as np
import sys

sys.path.append("F:/Python/EnsightTools")

from tools import *

simulation_list = ['G:\\PCF_Simulations\\Fueled Center\\Top_03_e',
                   'G:\\PCF_Simulations\\Fueled Center\\High_02_e',
                   'G:\\PCF_Simulations\\Fueled Center\\Low_03_e',
                   'G:\\PCF_Simulations\\Fueled Center\\Bottom_02_e',
                   'G:\\PCF_Simulations\\Fueled Forward\\Top_FF_e',
                   'G:\\PCF_Simulations\\Fueled Forward\\High_FF_e',
                   'G:\\PCF_Simulations\\Fueled Forward\\Low_FF_e',
                   'G:\\PCF_Simulations\\Fueled Forward\\Bot_FF_e',
                   'G:\\PCF_Simulations\\Unfueled Forward\\Top_UF',
                   'G:\\PCF_Simulations\\Unfueled Forward\\High_UF',
                   'G:\\PCF_Simulations\\Unfueled Forward\\Low_UF',
                   'G:\\PCF_Simulations\\Unfueled Forward\\Bot_UF']

units_list = ['K','m/s','m^2/s^2',' ', ' ', ' ', ' ']
variable_list = ['TEMPERATURE','VELOCITY','TKE','MASSFRAC_C3H8','MASSFRAC_CO2',
                 'MASSFRAC_OH','LAMBDA']

step_dt = .00002


# FUNCTIONALITY CHECK, TRUNCATED NUMBER OF SIMULATIONS AND VARIABLES

simulation_list = ['G:\\PCF_Simulations\\Fueled Center\\Top_03_e',
                   'G:\\PCF_Simulations\\Unfueled Forward\\Bot_UF']

variable_list = ['TEMPERATURE','VELOCITY']

units_list = ['K','m/s']


bulk_min_max_query(simulation_list,variable_list,units_list,step_dt)




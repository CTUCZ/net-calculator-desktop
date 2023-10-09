# -*- coding: utf-8 -*-
"""
Calculations and value preparations for presentation.
"""

import numpy as np
from scipy.stats import poisson

def calculate_UF(nbr_max, nbr_avg):
    """ Calculates required result in raw form """
    #nbr_max = self.ui.nbr_max.value()
    #nbr_avg = self.ui.nbr_avg.value()
    return nbr_avg/nbr_max

def prepare_UF(nbr_max, nbr_avg):
    """ Prepare calculated value for presentation in GUI"""
    output_UF = calculate_UF(nbr_max, nbr_avg)
    output_UF = np.round(output_UF, 3)
    
    #output_UF = f"{ self.calculate_UF(): n }" # initial value calculated ------ ValueError: Invalid format specifier
    #output_UF = str(self.calculate_UF()).format(",n") ) # initial value calculated ------ neudela se u initial ale u updatu ok
    output_UF = str(output_UF).replace(".",",") # hardcoded CZ format with comma, locale not working
    #output_UF = str(output_UF)
    
    return output_UF



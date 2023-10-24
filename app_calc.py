# -*- coding: utf-8 -*-
"""
Calculations and value preparations for presentation in GUI fields.
"""

from scipy.stats import poisson


def prepare_float(raw_float, round_decimals):
    """ Factory function for preparation of value to desired form for presentation in GUI. """
    out_val = round(raw_float, round_decimals)
    
    #out_val = f"{ out_val: n }" # ValueError: Invalid format specifier
    #out_val = str( out_val ).format(",n") ) 
    out_val = str(out_val).replace(".",",") # hardcoded CZ format with comma, locale not working
    #out_val = str(out_val)
    
    return out_val

def calculate_LU_max(capacity_L1, nbr_max):
    """ Calculates Link Utilization in raw form. """
    return nbr_max / capacity_L1

def calculate_UF(nbr_max, nbr_avg):
    """ Calculates Utilization Factor in raw form. """
    return nbr_avg/nbr_max

def prepare_UF(nbr_max, nbr_avg):
    """ Utilizaton factor for presentation in app GUI. """
    output_UF = calculate_UF(nbr_max, nbr_avg)    
    output_UF = prepare_float(output_UF, 3)
    
    return output_UF

def calculate_capacity_L4(capacity_L1, mtu, ipheader):
    """ L4 capacity for further use in other calculations. """
    capacity_L4 = ( capacity_L1 / ((mtu+38)*8) ) * (mtu-20-ipheader) * 8  # 20 is ipheader of L4
    
    return capacity_L4

def calculate_NBR_avg_L4(mtu, ipheader, nbr_avg):
    """ L4 average NBR (Net BitRate) for further use in other calculations. """
    nbr_avg_L4 = ( nbr_avg / ((mtu+38)*8) ) * (mtu-20-ipheader) * 8
    
    return nbr_avg_L4

def aggregation_estimated(capacity_L4, rsa_req):
    """ Estimated aggregation for further use in other calculations. """
    agg_est = int(capacity_L4 / rsa_req)   
    
    return agg_est


def calculate_lambda_RSA_noUF(prob, agg): 
    """ Calculates expected value lambda (mean number of occurences) for further use in RSA without Utilization Factor calculation.
    Searching the lambda given probability of occurence and number of events. """
    # The Poisson parameter Lambda (lam) is the total number of events (k) divided by the number of units (n) in the data (lam = k/n).
    # https://stackoverflow.com/questions/69455797/better-way-to-calculate-%CE%BB-in-a-poisson-distribution-if-the-probability-of-occurr
    # x_lam = -np.log(1-prob) # analytically only for prob=0 ???
    
    round_decimals = 6
    precision = 1 / (10**round_decimals) # smallest step must be compatible with rounding precision
    
    # "optimized" brute force: from "biggest" reasonable step to small step to have good final precision and low number of steps
    step = 100 # big enough step in the start of searching
    x_lambda = 0
    
    # fining the result till desired precision
    while (step >= precision):
        # searching with given precision
        
        while round(poisson.cdf(k=agg/(x_lambda + step), mu=(x_lambda + step)), round_decimals) > round(prob, round_decimals):
            x_lambda += step
        step /= 10 # lowering the order of step and continue with better precision
    
    return x_lambda

def calculate_RSA_noUF(capacity_L1, mtu, ipheader, agg, prob):
    """ Calculates RSA (Real Speed Achieved) without impact of Utilization Factor according to the methodics of CTO. """
    capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
    lam = calculate_lambda_RSA_noUF(prob, agg)
    RSA = capacity_L4 * lam / agg
    
    return RSA

def prepare_RSA_noUF(capacity_L1, mtu, ipheader, agg, prob): 
    """ RSA (Real Speed Achieved) without Utilization Factor for presentation in GUI. """
    output_RSA = calculate_RSA_noUF(capacity_L1, mtu, ipheader, agg, prob)
    output_RSA = prepare_float(output_RSA, 3)
    
    return output_RSA

    
def calculate_lambda_RSA_UF(prob, agg, lu_max): 
    """ Calculates expected value lambda (mean number of occurences) for further use in RSA with Utilization Factor calculation.
    Searching the lambda given probability of occurence and number of events. """
    
    round_decimals = 6
    precision = 1 / (10**round_decimals)
    
    # "optimized" brute force: from "biggest" reasonable step to small step to have good final precision and low number of steps
    step = 100 # big enough step in the start of searching
    x_lambda = 0
    
    # fining the result till desired precision
    while (step >= precision):
        # searching with given precision
        while round(poisson.cdf(k=( lu_max * (agg/(x_lambda + step)) ), mu=(x_lambda + step)), round_decimals) > round(prob, round_decimals):
            x_lambda += step
        step /= 10 # lowering the order of step and continue with better precision

    return x_lambda

def calculate_RSA_UF(capacity_L1, mtu, ipheader, agg, nbr_max, nbr_avg, prob):
    """ Calculates RSA (Real Speed Achieved) with impact of Utilization Factor according to the methodics of CTO. """
    lu_max = calculate_LU_max(capacity_L1, nbr_max)
    capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
    lam = calculate_lambda_RSA_UF(prob, agg, lu_max)
    uf = calculate_UF(nbr_max, nbr_avg)
    nbr_avg_L4 = calculate_NBR_avg_L4(mtu, ipheader, nbr_avg)
    RSA = (uf * capacity_L4**2 * lam) / (agg * nbr_avg_L4)
    
    return RSA

def prepare_RSA_UF(capacity_L1, mtu, ipheader, agg, nbr_max, nbr_avg, prob): 
    """ RSA (Real Speed Achieved) with Utilization Factor for presentation in GUI. """
    output_RSA = calculate_RSA_UF(capacity_L1, mtu, ipheader, agg, nbr_max, nbr_avg, prob)
    output_RSA = prepare_float(output_RSA, 3)
    
    return output_RSA


def calculate_RSA_agg(capacity_L1, mtu, ipheader, agg):
    """ Calculates RSA (Real Speed Achieved) with impact of natural aggregation according to the methodics of CTO. """
    capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
    RSA = capacity_L4 / agg
    
    return RSA

def prepare_RSA_agg(capacity_L1, mtu, ipheader, agg):
    """ RSA (Real Speed Achieved) with impact of natural aggregation for presentation in GUI. """
    output_RSA = calculate_RSA_agg(capacity_L1, mtu, ipheader, agg)
    output_RSA = prepare_float(output_RSA, 3)
    
    return output_RSA


def calculate_lambda_NTP(prob, agg): 
    """ Calculates expected value lambda (mean number of occurences) for further use in NTP with/without Utilization Factor calculation.
    Searching the lambda given probability of occurence and number of events. """
    
    round_decimals = 6
    precision = 1 / (10**round_decimals)
    
    # "optimized" brute force: from "biggest" reasonable step to small step to have good final precision and low number of steps
    step = 100 # big enough step in the start of searching
    x_lambda = 0
    
    # fining the result till desired precision
    while (step >= precision):
        #print("searching with step ", step)
        
        # searching with given precision
        while round(poisson.cdf(k=agg, mu=(x_lambda + step)), round_decimals) > round(prob, round_decimals):
            x_lambda += step
        
        step /= 10 # lowering the order of step and continue with better precision
    
    return x_lambda


def calculate_NTP_noUF(capacity_L1, mtu, ipheader, prob, rsa_req):
    """ Calculates NTP (Net Termination Points) without impact of Utilization Factor according to the methodics of CTO. """
    capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
    agg_est = aggregation_estimated(capacity_L4, rsa_req)
    lam = calculate_lambda_NTP(prob, agg_est)
    NTP = capacity_L4 * (lam/rsa_req)
    
    return NTP

def prepare_NTP_noUF(capacity_L1, mtu, ipheader, prob, rsa_req):
    """ NTP (Net Termination Points) without Utilization Factor for presentation in GUI. """
    output_NTP = calculate_NTP_noUF(capacity_L1, mtu, ipheader, prob, rsa_req)
    output_NTP = str(int(output_NTP))
    
    return output_NTP


def calculate_NTP_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req):
    """ Calculates NTP (Net Termination Points) with impact of Utilization Factor according to the methodics of CTO. """
    capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
    agg_est = aggregation_estimated(capacity_L4, rsa_req)
    lam = calculate_lambda_NTP(prob, agg_est)
    nbr_avg_L4 = calculate_NBR_avg_L4(mtu, ipheader, nbr_avg)
    uf = calculate_UF(nbr_max, nbr_avg)
    NTP = (uf * capacity_L4**2 * lam) / (rsa_req * nbr_avg_L4)
    
    return NTP

def prepare_NTP_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req):
    """ NTP (Net Termination Points) with Utilization Factor for presentation in GUI. """
    output_NTP = calculate_NTP_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req)
    output_NTP = str(int(output_NTP))
    
    return output_NTP


def calculate_perf_decrease_noUF(capacity_L1, mtu, ipheader, prob, rsa_req):
    """ Calculates service performance decrease without impact of Utilization Factor according to the methodics of CTO. """
    capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
    agg_est = aggregation_estimated(capacity_L4, rsa_req)
    lam = calculate_lambda_NTP(prob, agg_est)
    rsa_max = capacity_L4 / lam
    rsa_sigma = rsa_max - rsa_req
    perf_decrease = (rsa_sigma / rsa_max) * 100 
    
    return perf_decrease

def prepare_perf_decrease_noUF(capacity_L1, mtu, ipheader, prob, rsa_req):
    """ Service performance decrease without Utilization Factor for presentation in GUI. """
    output_perf = calculate_perf_decrease_noUF(capacity_L1, mtu, ipheader, prob, rsa_req)
    output_perf = prepare_float(output_perf, 3)
    
    return output_perf


def calculate_perf_decrease_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req):
    """ Calculates service performance decrease with impact of Utilization Factor according to the methodics of CTO. """
    capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
    nbr_avg_L4 = calculate_NBR_avg_L4(mtu, ipheader, nbr_avg)
    uf = calculate_UF(nbr_max, nbr_avg)
    ntp_est = int( (uf * capacity_L4**2)/(rsa_req * nbr_avg_L4) )
    lam = calculate_lambda_NTP(prob, ntp_est)
    rsa_max = (uf * capacity_L4**2) / (lam * nbr_avg_L4)
    rsa_sigma = rsa_max - rsa_req
    perf_decrease = (rsa_sigma / rsa_max) * 100 
    
    return perf_decrease

def prepare_perf_decrease_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req):
    """ Service performance decrease without Utilization Factor for presentation in GUI. """
    output_perf = calculate_perf_decrease_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req)
    output_perf = prepare_float(output_perf, 3)
    
    return output_perf

"""
agg = 256
prob = 0.9
capacity_L1 = 2488
mtu = 1500
ipheader = 20
nbr_max = 1000
nbr_avg = 500
sdr_req = 100


calculate_lambda_NTP(prob, agg)

lu_max = calculate_LU_max(capacity_L1, nbr_max)
calculate_lambda_RSA_UF(prob, agg, lu_max)

calculate_lambda_RSA_noUF(prob, agg)
"""
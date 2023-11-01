# -*- coding: utf-8 -*-
"""
Calculations and value preparations for presentation in GUI fields.
"""

from scipy.stats import poisson


def prepare_float(raw_float, round_decimals):
    """ Factory function for preparation of float value to desired form for presentation in GUI. """
    out_val = round(raw_float, round_decimals)
    
    #out_val = f"{out_val:.4n}" # exponential format with comma as decimal separator
    out_val = f"{out_val:,}".replace(",", "X").replace(".", ",").replace("X", " ") # hardcoded CZ format with comma, locale not working
    #out_val = str(out_val).replace(".",",") 
    #out_val = str(out_val)
    
    return out_val

def prepare_int(raw_num):
    """ Factory function for preparation of integer value to desired form for presentation in GUI. """
    out_val = f"{int(raw_num):,}".replace(",", " ") # thousand separator when integer
    
    return out_val

def calculate_LU_max(capacity_L1, nbr_max):
    """ Calculates Maximal Link Utilization in raw form. """
    return nbr_max / capacity_L1

def prepare_LU_max(capacity_L1, nbr_max): 
    """ Max LU (Link Utilization) for presentation in GUI. """
    output_LU = calculate_LU_max(capacity_L1, nbr_max)
    output_LU = prepare_float(output_LU, 2)
    
    return output_LU


def calculate_LU_avg(capacity_L1, nbr_avg):
    """ Calculates Average Link Utilization in raw form. """
    return nbr_avg / capacity_L1

def prepare_LU_avg(capacity_L1, nbr_avg): 
    """ Avg LU (Link Utilization) for presentation in GUI. """
    output_LU = calculate_LU_avg(capacity_L1, nbr_avg)
    output_LU = prepare_float(output_LU, 2)
    
    return output_LU


def calculate_UF(nbr_max, nbr_avg):
    """ Calculates Utilization Factor in raw form. """
    return nbr_avg/nbr_max

def prepare_UF(nbr_max, nbr_avg):
    """ Utilizaton factor for presentation in app GUI. """
    output_UF = calculate_UF(nbr_max, nbr_avg)    
    output_UF = prepare_float(output_UF, 2)
    
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


def calculate_lambda_div(prob, agg): 
    """ Calculates expected value lambda (mean number of occurences) as num1/num vs. num for further use in other calculations.
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
    """ Calculates L4 RSA (Real Speed Achieved) without impact of Utilization Factor according to the methodics of CTO. """
    capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
    lam = calculate_lambda_div(prob, agg)
    RSA = capacity_L4 * lam / agg
    
    return RSA

def prepare_RSA_noUF(capacity_L1, mtu, ipheader, agg, prob): 
    """ RSA (Real Speed Achieved) without Utilization Factor for presentation in GUI. """
    output_RSA = calculate_RSA_noUF(capacity_L1, mtu, ipheader, agg, prob)
    output_RSA = prepare_float(output_RSA, 1)
    
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
    """ Calculates L4 RSA (Real Speed Achieved) with impact of Utilization Factor according to the methodics of CTO. """
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
    output_RSA = prepare_float(output_RSA, 1)
    
    return output_RSA


# # not used in new version
# def calculate_BW_noUF(capacity_L1, mtu, ipheader, agg, prob):
#     """ Calculates L3 BW (BandWidth) without impact of Utilization Factor according to the methodics of CTO. """
#     rsa = calculate_RSA_noUF(capacity_L1, mtu, ipheader, agg, prob)
#     BW = (rsa * (mtu - ipheader)) / (mtu - ipheader - 20)
#    
#     return BW

# def prepare_BW_noUF(capacity_L1, mtu, ipheader, agg, prob): 
#     """ BW (BandWidth) without Utilization Factor for presentation in GUI. """
#     output_BW = calculate_BW_noUF(capacity_L1, mtu, ipheader, agg, prob)
#     output_BW = prepare_float(output_BW, 1)
#    
#     return output_BW

# # not used in new version
# def calculate_BW_UF(capacity_L1, mtu, ipheader, agg, nbr_max, nbr_avg, prob):
#     """ Calculates L3 BW (BandWidth) with impact of Utilization Factor according to the methodics of CTO. """
#     rsa = calculate_RSA_UF(capacity_L1, mtu, ipheader, agg, nbr_max, nbr_avg, prob)
#     BW = (rsa * (mtu - ipheader)) / (mtu - ipheader - 20)
#    
#     return BW

# def prepare_BW_UF(capacity_L1, mtu, ipheader, agg, nbr_max, nbr_avg, prob): 
#     """ BW (BandWidth) with Utilization Factor for presentation in GUI. """
#     output_BW = calculate_BW_UF(capacity_L1, mtu, ipheader, agg, nbr_max, nbr_avg, prob)
#     output_BW = prepare_float(output_BW, 1)
#    
#     return output_BW

# # not used in new version
# def calculate_RSA_agg(capacity_L1, mtu, ipheader, agg):
#     """ Calculates RSA (Real Speed Achieved) with impact of natural aggregation according to the methodics of CTO. """
#     capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
#     RSA = capacity_L4 / agg
#
#     return RSA

# # not used in new version
# def prepare_RSA_agg(capacity_L1, mtu, ipheader, agg):
#     """ RSA (Real Speed Achieved) with impact of natural aggregation for presentation in GUI. """
#     output_RSA = calculate_RSA_agg(capacity_L1, mtu, ipheader, agg)
#     output_RSA = prepare_float(output_RSA, 1)
#    
#     return output_RSA


def calculate_lambda_simple(prob, agg): 
    """ Calculates expected value lambda (mean number of occurences) as number vs. number for further use in other calculations.
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
    lam = calculate_lambda_simple(prob, agg_est)
    NTP = capacity_L4 * (lam/rsa_req)
    
    return NTP

def prepare_NTP_noUF(capacity_L1, mtu, ipheader, prob, rsa_req):
    """ NTP (Net Termination Points) without Utilization Factor for presentation in GUI. """
    output_NTP = calculate_NTP_noUF(capacity_L1, mtu, ipheader, prob, rsa_req)
    output_NTP = prepare_int(output_NTP)
    
    return output_NTP


def calculate_NTP_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req):
    """ Calculates NTP (Net Termination Points) with impact of Utilization Factor according to the methodics of CTO. """
    capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
    agg_est = aggregation_estimated(capacity_L4, rsa_req)
    lam = calculate_lambda_simple(prob, agg_est)
    nbr_avg_L4 = calculate_NBR_avg_L4(mtu, ipheader, nbr_avg)
    uf = calculate_UF(nbr_max, nbr_avg)
    NTP = (uf * capacity_L4**2 * lam) / (rsa_req * nbr_avg_L4)
    
    return NTP

def prepare_NTP_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req):
    """ NTP (Net Termination Points) with Utilization Factor for presentation in GUI. """
    output_NTP = calculate_NTP_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req)
    output_NTP = prepare_int(output_NTP)
    
    return output_NTP


def calculate_perf_decrease_noUF(capacity_L1, mtu, ipheader, prob, rsa_req):
    """ Calculates service performance decrease without impact of Utilization Factor according to the methodics of CTO. """
    capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
    agg_est = aggregation_estimated(capacity_L4, rsa_req)
    lam = calculate_lambda_simple(prob, agg_est)
    rsa_max = capacity_L4 / lam
    rsa_sigma = rsa_max - rsa_req
    perf_decrease = (rsa_sigma / rsa_max) * 100 
    
    return perf_decrease

def prepare_perf_decrease_noUF(capacity_L1, mtu, ipheader, prob, rsa_req):
    """ Service performance decrease without Utilization Factor for presentation in GUI. """
    output_perf = calculate_perf_decrease_noUF(capacity_L1, mtu, ipheader, prob, rsa_req)
    output_perf = prepare_float(output_perf, 1)
    
    return output_perf


def calculate_perf_decrease_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req):
    """ Calculates service performance decrease with impact of Utilization Factor according to the methodics of CTO. """
    capacity_L4 = calculate_capacity_L4(capacity_L1, mtu, ipheader)
    nbr_avg_L4 = calculate_NBR_avg_L4(mtu, ipheader, nbr_avg)
    uf = calculate_UF(nbr_max, nbr_avg)
    ntp_est = int( (uf * capacity_L4**2)/(rsa_req * nbr_avg_L4) )
    lam = calculate_lambda_simple(prob, ntp_est)
    rsa_max = (uf * capacity_L4**2) / (lam * nbr_avg_L4)
    rsa_sigma = rsa_max - rsa_req
    perf_decrease = (rsa_sigma / rsa_max) * 100 
    
    return perf_decrease

def prepare_perf_decrease_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req):
    """ Service performance decrease without Utilization Factor for presentation in GUI. """
    output_perf = calculate_perf_decrease_UF(capacity_L1, mtu, ipheader, nbr_max, nbr_avg, prob, rsa_req)
    output_perf = prepare_float(output_perf, 1)
    
    return output_perf


def calculate_BW_min(mtu, ipheader, agg, prob, rsa_req):
    """ Calculates L3 minimal bandwidth of bottleneck according to the methodics of CTO. """
    lam = calculate_lambda_div(prob, agg)
    BW = ( (rsa_req * (agg / lam)) * (mtu - ipheader) ) / (mtu - ipheader - 8)
    
    return BW

def prepare_BW_min(mtu, ipheader, agg, prob, rsa_req):
    """ L3 minimal bandwidth for presentation in GUI. """
    output_BW = calculate_BW_min(mtu, ipheader, agg, prob, rsa_req)
    output_BW = prepare_float(output_BW, 1)
    
    return output_BW


def calculate_capacity_min(mtu, ipheader, agg, nbr_max, nbr_avg, prob, rsa_req):
    """ Calculates L3 minimal capacity of bottleneck according to the methodics of CTO. """
    uf = calculate_UF(nbr_max, nbr_avg)
    lam = calculate_lambda_div(prob, agg)
    capacity_L3 = ( ( ( (rsa_req * agg * nbr_avg) / (uf * lam) )**0.5 ) * (mtu - ipheader) ) / (mtu - ipheader - 8)
    
    return capacity_L3

def prepare_capacity_min(mtu, ipheader, agg, nbr_max, nbr_avg, prob, rsa_req):
    """ L3 minimal capacity for presentation in GUI. """
    output_cap = calculate_capacity_min(mtu, ipheader, agg, nbr_max, nbr_avg, prob, rsa_req)
    output_cap = prepare_float(output_cap, 1)
    
    return output_cap


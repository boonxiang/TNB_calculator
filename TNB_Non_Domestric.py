#!/usr/bin/env python
# coding: utf-8

import math


# # EEI and Rate



TNB_Non_Domestic_RATES = {
    'low_General': {  
        'energy' :0.2703,      # 27.03 sen/kwh
        'capacity': 0.0883,    # 8.83 sen/kWh
        'network': 0.1482,     # 14.82 sen/kWh
        'retail': 20.00        # RM 20.00/month
    },
    'low_TOU': {  
        'peak': 0.2852,        # 28.52 sen/kWh
        'off_peak': 0.2443,    # 24.43 sen/kWh
        'capacity': 0.0883,    # 8.83 sen/kWh
        'network': 0.1482,     # 14.82 sen/kWh
        'retail': 20.00        # RM 10.00/month
    },
    'medium_General': {  
        'energy' :0.2983,      # 29.83 sen/kwh
        'capacity': 29.43,    # 29.43 RM/kWh
        'network': 59.84,     # 59.84 RM/kWh
        'retail': 200.00        # RM 200.00/month
    },
    'medium_TOU': {  
        'peak': 0.3132,        # 31.32 sen/kWh
        'off_peak': 0.2723,    # 27.23 sen/kWh
        'capacity': 30.19,    # 30.19 RM/kWh
        'network': 66.87,     # 66.87 RM/kWh
        'retail': 200.00        # RM 200.00/month
    },
    'high_General': {  
        'energy' :0.4303,      # 43.03 sen/kwh
        'capacity': 16.68,    # 16.68 RM/kWh
        'network': 14.53,     # 14.53 RM/kWh
        'retail': 250.00        # RM 250.00/month
    },
    'high_TOU': {  
        'peak': 0.4452,        # 44.52 sen/kWh
        'off_peak': 0.4043,    # 40.43 sen/kWh
        'capacity': 21.76,    # 21.76 RM/kWh
        'network': 23.06,     # 23.06 RM/kWh
        'retail': 250.00        # RM 250.00/month
    }
}


# In[12]:


def calculate_eei(total_kwh):
    """
    EEI rebate uses a single slab rate based on total_kwh.
    Entire usage gets the slab's rate.
    """
    if total_kwh <= 200:
        return 0.11
    else:
        return 0
    


# # Non-Domestic Low General
def calculate_bill_from_usage_nd_low_general(total_usage):
    """Calculate electricity bill where peak usage is input as a percentage"""
    # Convert percentage to actual kWh
    
    rates = TNB_Non_Domestic_RATES['low_General'] 

    # Energy Efficiency Incentive (rebate is applied to total_usage)
    eei_rebate_rate = calculate_eei(total_usage)

    energy = total_usage* rates['energy']
    capacity = total_usage * rates['capacity']
    network = total_usage * rates['network']
    retail = rates['retail'] 
    eei_rebate = total_usage * eei_rebate_rate
    subtotal = energy + capacity + network + retail - eei_rebate
    
    kwtbb = (subtotal - retail) * 0.016
  
    total_bill = subtotal + kwtbb

    # Round everything to 2 decimal points
    return {
        'total_usage': round(total_usage, 2),
        'energy_total': round(energy, 2),
        'capacity_total': round(capacity, 2),
        'network_total': round(network, 2),
        'retail_total': round(retail, 2),
        'eei_rebate': round(eei_rebate, 2),
        'subtotal': round(subtotal, 2),
        'kwtbb': round(kwtbb, 2),
        'total_bill': round(total_bill, 2)
    }


# In[14]:


calculate_bill_from_usage_nd_low_general(200)


# In[15]:


def reverse_tnb_nd_general_bill(total_bill_input,tolerance=0.01, max_kwh=10000000):
    import math

    low = 1.0
    high = max_kwh * 1.0
    guess = (low + high) / 2

    iterations = 0
    max_iterations = 100

    best_guess = None
    min_diff = float('inf')

    while iterations < max_iterations:
        result = calculate_bill_from_usage_nd_low_general(guess)
        calculated_bill = result['total_bill']
        difference = calculated_bill - total_bill_input

        if abs(difference) < min_diff:
            min_diff = abs(difference)
            best_guess = (guess, result)

        if abs(difference) <= tolerance:
            return {
                'estimated_total_kwh': round(guess, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'energy_total': result['energy_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'retail_charge': result['retail_total'],
                'kwtbb': result['kwtbb'],
                'eei_rebate': result['eei_rebate'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_within_tolerance'
            }

        if calculated_bill < total_bill_input:
            low = guess
        else:
            high = guess

        guess = (low + high) / 2
        iterations += 1

    # Fine-tune scan ±2 kWh
    for adj in [x / 10.0 for x in range(-20, 21)]:
        refined_kwh = best_guess[0] + adj
        if refined_kwh < 0:
            continue
        result = calculate_bill_from_usage_nd_low_general(refined_kwh)
        calculated_bill = result['total_bill']
        diff = abs(calculated_bill - total_bill_input)
        if diff <= tolerance:
            return {
                'estimated_total_kwh': round(refined_kwh, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'energy_total': result['energy_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'retail_charge': result['retail_total'],
                'kwtbb': result['kwtbb'],
                'eei_rebate': result['eei_rebate'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_in_fine_scan'
            }

    # Final fallback: return best guess even if not matched
    best_kwh = round(best_guess[0], 2)
    best_result = best_guess[1]

    return {
        'error': 'No match found within tolerance.',
        'best_guess_kwh': best_kwh,
        'best_matched_bill': best_result['total_bill'],
        'energy_total': best_result['energy_total'],
        'network_charge': best_result['network_total'],
        'capacity_charge': best_result['capacity_total'],
        'retail_charge': best_result['retail_total'],
        'kwtbb': best_result['kwtbb'],
        'eei_rebate': best_result['eei_rebate'],
        'subtotal': best_result['subtotal'],
        'difference': round(abs(best_result['total_bill'] - total_bill_input), 2),
        'iterations': iterations
    }


# In[22]:


reverse_tnb_nd_general_bill(100)


# # Non-Domestic Low TOU

# In[17]:


def calculate_bill_from_usage_nd_TOU(total_usage, peak_percent):
    """Calculate electricity bill where peak usage is input as a percentage"""
    # Convert percentage to actual kWh
    peak_usage = total_usage * (peak_percent / 100)
    off_peak_usage = total_usage - peak_usage

    rates = TNB_Non_Domestic_RATES['low_TOU'] 

    # Energy Efficiency Incentive (rebate is applied to total_usage)
    eei_rebate_rate = calculate_eei(total_usage)
  
    
    energy_peak = peak_usage * rates['peak']
    energy_off_peak = off_peak_usage * rates['off_peak']
    capacity = total_usage * rates['capacity']
    network = total_usage * rates['network']
    retail = rates['retail']
    eei_rebate = total_usage * eei_rebate_rate
    subtotal = energy_peak + energy_off_peak + capacity + network + retail - eei_rebate

    kwtbb = (subtotal - retail) * 0.016
  

    total_bill = subtotal + kwtbb

    # Round everything to 2 decimal points
    return {
        'total_usage': round(total_usage, 2),
        'peak_percent': round(peak_percent, 2),
        'peak_usage_kwh': round(peak_usage, 2),
        'off_peak_usage_kwh': round(off_peak_usage, 2),

        'energy_peak_total': round(energy_peak, 2),
        'energy_off_peak_total': round(energy_off_peak, 2),
        'capacity_total': round(capacity, 2),
        'network_total': round(network, 2),
        'retail_total': round(retail, 2),

        'eei_rebate': round(eei_rebate, 2),
        'subtotal': round(subtotal, 2),
      
        'kwtbb': round(kwtbb, 2),
        'total_bill': round(total_bill, 2)
    }


# In[23]:


calculate_bill_from_usage_nd_TOU(100, 10)


# In[19]:


def reverse_tnb_nd_tou_bill(total_bill_input, peak_percent, tolerance=0.01, max_kwh=5000):

    low = 1.0
    high = max_kwh * 1.0
    guess = (low + high) / 2

    iterations = 0
    max_iterations = 100

    best_guess = None
    min_diff = float('inf')

    while iterations < max_iterations:
        result = calculate_bill_from_usage_nd_TOU(guess, peak_percent)
        calculated_bill = result['total_bill']
        difference = calculated_bill - total_bill_input

        if abs(difference) < min_diff:
            min_diff = abs(difference)
            best_guess = (guess, result)

        if abs(difference) <= tolerance:
            return {
                'estimated_total_kwh': round(guess, 2),
                'estimated_peak_kwh': round(result['peak_usage_kwh'], 2),
                'estimated_off_peak_kwh': round(result['off_peak_usage_kwh'], 2),
                'peak_percent': round(peak_percent, 2),
                'off_peak_percent': round(100 - peak_percent, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'kwtbb': result['kwtbb'],
                'retail_charge': result['retail_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'energy_peak_total': result['energy_peak_total'],
                'energy_off_peak_total': result['energy_off_peak_total'],
                'eei_rebate': result['eei_rebate'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_within_tolerance'
            }

        if calculated_bill < total_bill_input:
            low = guess
        else:
            high = guess

        guess = (low + high) / 2
        iterations += 1

    # Fine-tune scan ±2 kWh
    for adj in [x / 10.0 for x in range(-20, 21)]:
        refined_kwh = best_guess[0] + adj
        if refined_kwh < 0:
            continue
        result = calculate_bill_from_usage_nd_TOU(refined_kwh, peak_percent)
        calculated_bill = result['total_bill']
        diff = abs(calculated_bill - total_bill_input)
        if diff <= tolerance:
            return {
                'estimated_total_kwh': round(refined_kwh, 2),
                'estimated_peak_kwh': round(result['peak_usage_kwh'], 2),
                'estimated_off_peak_kwh': round(result['off_peak_usage_kwh'], 2),
                'peak_percent': round(peak_percent, 2),
                'off_peak_percent': round(100 - peak_percent, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'kwtbb': result['kwtbb'],
                'retail_charge': result['retail_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'energy_peak_total': result['energy_peak_total'],
                'energy_off_peak_total': result['energy_off_peak_total'],
                'eei_rebate': result['eei_rebate'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_in_fine_scan'
            }

    # Final fallback: return best guess even if not matched
    best_kwh = round(best_guess[0], 2)
    best_result = best_guess[1]
    best_peak_kwh = math.ceil(best_kwh * (peak_percent / 100))
    best_off_peak_kwh = math.ceil(best_kwh - best_peak_kwh)

    return {
        'error': 'No match found within tolerance.',
        'best_guess_kwh': best_kwh,
        'estimated_peak_kwh': best_peak_kwh,
        'estimated_off_peak_kwh': best_off_peak_kwh,
        'peak_percent': round(peak_percent, 2),
        'off_peak_percent': round(100 - peak_percent, 2),
        'best_matched_bill': best_result['total_bill'],
        'kwtbb': best_result['kwtbb'],
        'retail_charge': best_result['retail_total'],
        'network_charge': best_result['network_total'],
        'capacity_charge': best_result['capacity_total'],
        'energy_peak_total': best_result['energy_peak_total'],
        'energy_off_peak_total': best_result['energy_off_peak_total'],
        'eei_rebate': best_result['eei_rebate'],
        'subtotal': best_result['subtotal'],
        'difference': round(abs(best_result['total_bill'] - total_bill_input), 2),
        'iterations': iterations
    }


# In[20]:


reverse_tnb_nd_tou_bill(266.32,10)


# # Non-Domestic Medium General

# In[44]:


def calculate_bill_from_usage_nd_medium_general(total_usage,maximum_demand):
    """Calculate electricity bill where peak usage is input as a percentage"""
    # Convert percentage to actual kWh
    
    rates = TNB_Non_Domestic_RATES['medium_General'] 

    energy = total_usage* rates['energy']
    capacity =  rates['capacity'] * maximum_demand
    network = rates['network'] * maximum_demand
    retail = rates['retail'] 
    subtotal = energy + capacity + network + retail
    
    kwtbb = (subtotal - retail) * 0.016
  
    total_bill = subtotal + kwtbb

    # Round everything to 2 decimal points
    return {
        'total_usage': round(total_usage, 2),
        'energy_total': round(energy, 2),
        'capacity_total': round(capacity, 2),
        'network_total': round(network, 2),
        'retail_total': round(retail, 2),
        'subtotal': round(subtotal, 2),
        'kwtbb': round(kwtbb, 2),
        'total_bill': round(total_bill, 2)
    }


# In[45]:


calculate_bill_from_usage_nd_medium_general(20,100)


# In[47]:


def reverse_tnb_nd_medium_general_bill(total_bill_input,maximum_demand,tolerance=0.01, max_kwh=10000000):

    low = 1.0
    high = max_kwh * 1.0
    guess = (low + high) / 2

    iterations = 0
    max_iterations = 100

    best_guess = None
    min_diff = float('inf')

    while iterations < max_iterations:
        result = calculate_bill_from_usage_nd_medium_general(guess,maximum_demand)
        calculated_bill = result['total_bill']
        difference = calculated_bill - total_bill_input

        if abs(difference) < min_diff:
            min_diff = abs(difference)
            best_guess = (guess, result)

        if abs(difference) <= tolerance:
            return {
                'estimated_total_kwh': round(guess, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'energy_total': result['energy_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'retail_charge': result['retail_total'],
                'kwtbb': result['kwtbb'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_within_tolerance'
            }

        if calculated_bill < total_bill_input:
            low = guess
        else:
            high = guess

        guess = (low + high) / 2
        iterations += 1

    # Fine-tune scan ±2 kWh
    for adj in [x / 10.0 for x in range(-20, 21)]:
        refined_kwh = best_guess[0] + adj
        if refined_kwh < 0:
            continue
        result = calculate_bill_from_usage_nd_medium_general(refined_kwh,maximum_demand)
        calculated_bill = result['total_bill']
        diff = abs(calculated_bill - total_bill_input)
        if diff <= tolerance:
            return {
                'estimated_total_kwh': round(refined_kwh, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'energy_total': result['energy_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'retail_charge': result['retail_total'],
                'kwtbb': result['kwtbb'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_in_fine_scan'
            }

    # Final fallback: return best guess even if not matched
    best_kwh = round(best_guess[0], 2)
    best_result = best_guess[1]

    return {
        'error': 'No match found within tolerance.',
        'best_guess_kwh': best_kwh,
        'best_matched_bill': best_result['total_bill'],
        'energy_total': best_result['energy_total'],
        'network_charge': best_result['network_total'],
        'capacity_charge': best_result['capacity_total'],
        'retail_charge': best_result['retail_total'],
        'kwtbb': best_result['kwtbb'],
        'subtotal': best_result['subtotal'],
        'difference': round(abs(best_result['total_bill'] - total_bill_input), 2),
        'iterations': iterations
    }


# In[48]:


reverse_tnb_nd_medium_general_bill(9275.89,100)


# # Non-Domestic Medium TOU

# In[50]:


def calculate_bill_from_usage_nd_medium_TOU(total_usage, maximum_demand,peak_percent):
    """Calculate electricity bill where peak usage is input as a percentage"""
    # Convert percentage to actual kWh
    peak_usage = total_usage * (peak_percent / 100)
    off_peak_usage = total_usage - peak_usage

    rates = TNB_Non_Domestic_RATES['medium_TOU'] 

    
    energy_peak = peak_usage * rates['peak']
    energy_off_peak = off_peak_usage * rates['off_peak']
    capacity = maximum_demand * rates['capacity']
    network = maximum_demand * rates['network']
    retail = rates['retail']
    subtotal = energy_peak + energy_off_peak + capacity + network + retail 

    kwtbb = (subtotal - retail) * 0.016
  

    total_bill = subtotal + kwtbb

    # Round everything to 2 decimal points
    return {
        'total_usage': round(total_usage, 2),
        'peak_percent': round(peak_percent, 2),
        'peak_usage_kwh': round(peak_usage, 2),
        'off_peak_usage_kwh': round(off_peak_usage, 2),
        'energy_peak_total': round(energy_peak, 2),
        'energy_off_peak_total': round(energy_off_peak, 2),
        'capacity_total': round(capacity, 2),
        'network_total': round(network, 2),
        'retail_total': round(retail, 2),
        'subtotal': round(subtotal, 2),
        'kwtbb': round(kwtbb, 2),
        'total_bill': round(total_bill, 2)
    }
 


# In[55]:


calculate_bill_from_usage_nd_medium_TOU(10, 100,10)


# In[57]:


def reverse_tnb_nd_medium_tou_bill(total_bill_input,maximum_demand,peak_percent, tolerance=0.01, max_kwh=100000000):

    low = 1.0
    high = max_kwh * 1.0
    guess = (low + high) / 2

    iterations = 0
    max_iterations = 100

    best_guess = None
    min_diff = float('inf')

    while iterations < max_iterations:
        result = calculate_bill_from_usage_nd_medium_TOU(guess,maximum_demand,peak_percent)
        calculated_bill = result['total_bill']
        difference = calculated_bill - total_bill_input

        if abs(difference) < min_diff:
            min_diff = abs(difference)
            best_guess = (guess, result)

        if abs(difference) <= tolerance:
            return {
                'estimated_total_kwh': round(guess, 2),
                'estimated_peak_kwh': round(result['peak_usage_kwh'], 2),
                'estimated_off_peak_kwh': round(result['off_peak_usage_kwh'], 2),
                'peak_percent': round(peak_percent, 2),
                'off_peak_percent': round(100 - peak_percent, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'kwtbb': result['kwtbb'],
                'retail_charge': result['retail_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'energy_peak_total': result['energy_peak_total'],
                'energy_off_peak_total': result['energy_off_peak_total'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_within_tolerance'
            }

        if calculated_bill < total_bill_input:
            low = guess
        else:
            high = guess

        guess = (low + high) / 2
        iterations += 1

    # Fine-tune scan ±2 kWh
    for adj in [x / 10.0 for x in range(-20, 21)]:
        refined_kwh = best_guess[0] + adj
        if refined_kwh < 0:
            continue
        result = calculate_bill_from_usage_nd_medium_TOU(refined_kwh,maximum_demand,peak_percent)
        calculated_bill = result['total_bill']
        diff = abs(calculated_bill - total_bill_input)
        if diff <= tolerance:
            return {
                'estimated_total_kwh': round(refined_kwh, 2),
                'estimated_peak_kwh': round(result['peak_usage_kwh'], 2),
                'estimated_off_peak_kwh': round(result['off_peak_usage_kwh'], 2),
                'peak_percent': round(peak_percent, 2),
                'off_peak_percent': round(100 - peak_percent, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'kwtbb': result['kwtbb'],
                'retail_charge': result['retail_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'energy_peak_total': result['energy_peak_total'],
                'energy_off_peak_total': result['energy_off_peak_total'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_in_fine_scan'
            }

    # Final fallback: return best guess even if not matched
    best_kwh = round(best_guess[0], 2)
    best_result = best_guess[1]
    best_peak_kwh = math.ceil(best_kwh * (peak_percent / 100))
    best_off_peak_kwh = math.ceil(best_kwh - best_peak_kwh)

    return {
        'error': 'No match found within tolerance.',
        'best_guess_kwh': best_kwh,
        'estimated_peak_kwh': best_peak_kwh,
        'estimated_off_peak_kwh': best_off_peak_kwh,
        'peak_percent': round(peak_percent, 2),
        'off_peak_percent': round(100 - peak_percent, 2),
        'best_matched_bill': best_result['total_bill'],
        'kwtbb': best_result['kwtbb'],
        'retail_charge': best_result['retail_total'],
        'network_charge': best_result['network_total'],
        'capacity_charge': best_result['capacity_total'],
        'energy_peak_total': best_result['energy_peak_total'],
        'energy_off_peak_total': best_result['energy_off_peak_total'],
        'subtotal': best_result['subtotal'],
        'difference': round(abs(best_result['total_bill'] - total_bill_input), 2),
        'iterations': iterations
    }


# In[58]:


reverse_tnb_nd_medium_tou_bill(10064.10,100,10)


# # Non-Domestic High General

# In[59]:


def calculate_bill_from_usage_nd_high_general(total_usage,maximum_demand):
    """Calculate electricity bill where peak usage is input as a percentage"""
    # Convert percentage to actual kWh
    
    rates = TNB_Non_Domestic_RATES['high_General'] 

    energy = total_usage* rates['energy']
    capacity =  rates['capacity'] * maximum_demand
    network = rates['network'] * maximum_demand
    retail = rates['retail'] 
    subtotal = energy + capacity + network + retail
    
    kwtbb = (subtotal - retail) * 0.016
  
    total_bill = subtotal + kwtbb

    # Round everything to 2 decimal points
    return {
        'total_usage': round(total_usage, 2),
        'energy_total': round(energy, 2),
        'capacity_total': round(capacity, 2),
        'network_total': round(network, 2),
        'retail_total': round(retail, 2),
        'subtotal': round(subtotal, 2),
        'kwtbb': round(kwtbb, 2),
        'total_bill': round(total_bill, 2)
    }


# In[60]:


calculate_bill_from_usage_nd_high_general(100,10)


# In[61]:


def reverse_tnb_nd_high_general_bill(total_bill_input,maximum_demand,tolerance=0.01, max_kwh=10000000):
   
    low = 1.0
    high = max_kwh * 1.0
    guess = (low + high) / 2

    iterations = 0
    max_iterations = 100

    best_guess = None
    min_diff = float('inf')

    while iterations < max_iterations:
        result = calculate_bill_from_usage_nd_high_general(guess,maximum_demand)
        calculated_bill = result['total_bill']
        difference = calculated_bill - total_bill_input

        if abs(difference) < min_diff:
            min_diff = abs(difference)
            best_guess = (guess, result)

        if abs(difference) <= tolerance:
            return {
                'estimated_total_kwh': round(guess, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'energy_total': result['energy_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'retail_charge': result['retail_total'],
                'kwtbb': result['kwtbb'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_within_tolerance'
            }

        if calculated_bill < total_bill_input:
            low = guess
        else:
            high = guess

        guess = (low + high) / 2
        iterations += 1

    # Fine-tune scan ±2 kWh
    for adj in [x / 10.0 for x in range(-20, 21)]:
        refined_kwh = best_guess[0] + adj
        if refined_kwh < 0:
            continue
        result = calculate_bill_from_usage_nd_high_general(refined_kwh,maximum_demand)
        calculated_bill = result['total_bill']
        diff = abs(calculated_bill - total_bill_input)
        if diff <= tolerance:
            return {
                'estimated_total_kwh': round(refined_kwh, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'energy_total': result['energy_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'retail_charge': result['retail_total'],
                'kwtbb': result['kwtbb'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_in_fine_scan'
            }

    # Final fallback: return best guess even if not matched
    best_kwh = round(best_guess[0], 2)
    best_result = best_guess[1]

    return {
        'error': 'No match found within tolerance.',
        'best_guess_kwh': best_kwh,
        'best_matched_bill': best_result['total_bill'],
        'energy_total': best_result['energy_total'],
        'network_charge': best_result['network_total'],
        'capacity_charge': best_result['capacity_total'],
        'retail_charge': best_result['retail_total'],
        'kwtbb': best_result['kwtbb'],
        'subtotal': best_result['subtotal'],
        'difference': round(abs(best_result['total_bill'] - total_bill_input), 2),
        'iterations': iterations
    }


# In[62]:


reverse_tnb_nd_high_general_bill(610.81,10)


# # Non-Domestic High TOU

# In[64]:


def calculate_bill_from_usage_nd_high_TOU(total_usage, maximum_demand,peak_percent):
    """Calculate electricity bill where peak usage is input as a percentage"""
    # Convert percentage to actual kWh
    peak_usage = total_usage * (peak_percent / 100)
    off_peak_usage = total_usage - peak_usage

    rates = TNB_Non_Domestic_RATES['high_TOU'] 

    
    energy_peak = peak_usage * rates['peak']
    energy_off_peak = off_peak_usage * rates['off_peak']
    capacity = maximum_demand * rates['capacity']
    network = maximum_demand * rates['network']
    retail = rates['retail']
    subtotal = energy_peak + energy_off_peak + capacity + network + retail 

    kwtbb = (subtotal - retail) * 0.016
  

    total_bill = subtotal + kwtbb

    # Round everything to 2 decimal points
    return {
        'total_usage': round(total_usage, 2),
        'peak_percent': round(peak_percent, 2),
        'peak_usage_kwh': round(peak_usage, 2),
        'off_peak_usage_kwh': round(off_peak_usage, 2),
        'energy_peak_total': round(energy_peak, 2),
        'energy_off_peak_total': round(energy_off_peak, 2),
        'capacity_total': round(capacity, 2),
        'network_total': round(network, 2),
        'retail_total': round(retail, 2),
        'subtotal': round(subtotal, 2),
        'kwtbb': round(kwtbb, 2),
        'total_bill': round(total_bill, 2)
    }
 


# In[65]:


calculate_bill_from_usage_nd_high_TOU(100, 10,10)


# In[66]:


def reverse_tnb_nd_medium_tou_bill(total_bill_input,maximum_demand,peak_percent, tolerance=0.01, max_kwh=100000000):

    low = 1.0
    high = max_kwh * 1.0
    guess = (low + high) / 2

    iterations = 0
    max_iterations = 100

    best_guess = None
    min_diff = float('inf')

    while iterations < max_iterations:
        result = calculate_bill_from_usage_nd_high_TOU(guess,maximum_demand,peak_percent)
        calculated_bill = result['total_bill']
        difference = calculated_bill - total_bill_input

        if abs(difference) < min_diff:
            min_diff = abs(difference)
            best_guess = (guess, result)

        if abs(difference) <= tolerance:
            return {
                'estimated_total_kwh': round(guess, 2),
                'estimated_peak_kwh': round(result['peak_usage_kwh'], 2),
                'estimated_off_peak_kwh': round(result['off_peak_usage_kwh'], 2),
                'peak_percent': round(peak_percent, 2),
                'off_peak_percent': round(100 - peak_percent, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'kwtbb': result['kwtbb'],
                'retail_charge': result['retail_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'energy_peak_total': result['energy_peak_total'],
                'energy_off_peak_total': result['energy_off_peak_total'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_within_tolerance'
            }

        if calculated_bill < total_bill_input:
            low = guess
        else:
            high = guess

        guess = (low + high) / 2
        iterations += 1

    # Fine-tune scan ±2 kWh
    for adj in [x / 10.0 for x in range(-20, 21)]:
        refined_kwh = best_guess[0] + adj
        if refined_kwh < 0:
            continue
        result = calculate_bill_from_usage_nd_high_TOU(refined_kwh,maximum_demand,peak_percent)
        calculated_bill = result['total_bill']
        diff = abs(calculated_bill - total_bill_input)
        if diff <= tolerance:
            return {
                'estimated_total_kwh': round(refined_kwh, 2),
                'estimated_peak_kwh': round(result['peak_usage_kwh'], 2),
                'estimated_off_peak_kwh': round(result['off_peak_usage_kwh'], 2),
                'peak_percent': round(peak_percent, 2),
                'off_peak_percent': round(100 - peak_percent, 2),
                'matched_total_bill': round(calculated_bill, 2),
                'kwtbb': result['kwtbb'],
                'retail_charge': result['retail_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'energy_peak_total': result['energy_peak_total'],
                'energy_off_peak_total': result['energy_off_peak_total'],
                'subtotal': result['subtotal'],
                'iterations': iterations,
                'status': 'matched_in_fine_scan'
            }

    # Final fallback: return best guess even if not matched
    best_kwh = round(best_guess[0], 2)
    best_result = best_guess[1]
    best_peak_kwh = math.ceil(best_kwh * (peak_percent / 100))
    best_off_peak_kwh = math.ceil(best_kwh - best_peak_kwh)

    return {
        'error': 'No match found within tolerance.',
        'best_guess_kwh': best_kwh,
        'estimated_peak_kwh': best_peak_kwh,
        'estimated_off_peak_kwh': best_off_peak_kwh,
        'peak_percent': round(peak_percent, 2),
        'off_peak_percent': round(100 - peak_percent, 2),
        'best_matched_bill': best_result['total_bill'],
        'kwtbb': best_result['kwtbb'],
        'retail_charge': best_result['retail_total'],
        'network_charge': best_result['network_total'],
        'capacity_charge': best_result['capacity_total'],
        'energy_peak_total': best_result['energy_peak_total'],
        'energy_off_peak_total': best_result['energy_off_peak_total'],
        'subtotal': best_result['subtotal'],
        'difference': round(abs(best_result['total_bill'] - total_bill_input), 2),
        'iterations': iterations
    }


# In[67]:


reverse_tnb_nd_medium_tou_bill(746.86,10,10)


# In[ ]:





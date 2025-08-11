#!/usr/bin/env python
# coding: utf-8

# ## RATE AND EEI

# In[1]:


TNB_DOMESTRIC_RATES = {
    'low_general': {  # ≤1500 kWh
        'energy' :0.2703,      # 27.03 sen/kwh
        'capacity': 0.0455,    # 4.55 sen/kWh
        'network': 0.1285,     # 12.85 sen/kWh
        'retail': 10.00        # RM 10.00/month
    },
    'high_general': {  # >1500 kWh
        'energy' :0.3703,      # 37.03 sen/kwh
        'capacity': 0.0455,    # 4.55 sen/kWh
        'network': 0.1285,     # 12.85 sen/kWh
        'retail': 10.00        # RM 10.00/month
    },
    'low_TOU': {  # ≤1500 kWh
        'peak': 0.2852,        # 28.52 sen/kWh
        'off_peak': 0.2443,    # 24.43 sen/kWh
        'capacity': 0.0455,    # 4.55 sen/kWh
        'network': 0.1285,     # 12.85 sen/kWh
        'retail': 10.00        # RM 10.00/month
    },
    'high_TOU': {  # >1500 kWh
        'peak': 0.3852,        # 38.52 sen/kWh
        'off_peak': 0.3443,    # 34.43 sen/kWh
        'capacity': 0.0455,    # 4.55 sen/kWh
        'network': 0.1285,     # 12.85 sen/kWh
        'retail': 10.00        # RM 10.00/month
    }
}


# In[2]:


def calculate_eei_domestric(total_kwh):
    """
    EEI rebate uses a single slab rate based on total_kwh.
    Entire usage gets the slab's rate.
    """
    if total_kwh > 1000:
        return 0.0

    slabs = [
        (1, 200, 25.0),    # 25.0 sen/kWh rebate
        (201, 250, 24.5),  # 24.5 sen/kWh rebate
        (251, 300, 22.5),  # 22.5 sen/kWh rebate
        (301, 350, 21.0),  # 21.0 sen/kWh rebate
        (351, 400, 17.0),  # 17.0 sen/kWh rebate
        (401, 450, 14.5),  # 14.5 sen/kWh rebate
        (451, 500, 12.0),  # 12.0 sen/kWh rebate
        (501, 550, 10.5),  # 10.5 sen/kWh rebate
        (551, 600, 9.0),   # 9.0 sen/kWh rebate
        (601, 650, 7.5),   # 7.5 sen/kWh rebate
        (651, 700, 5.5),   # 5.5 sen/kWh rebate
        (701, 750, 4.5),   # 4.5 sen/kWh rebate
        (751, 800, 4.0),   # 4.0 sen/kWh rebate
        (801, 850, 2.5),   # 2.5 sen/kWh rebate
        (851, 900, 1.0),   # 1.0 sen/kWh rebate
        (901, 1000, 0.5),  # 0.5 sen/kWh rebate
    ]

    for lower, upper, rate_sen in slabs:
        if lower <= total_kwh <= upper:
            rebate_rm = total_kwh * (rate_sen / 100)  # Convert sen to RM
            return round(rebate_rm, 2)

    return 0.0


# ## General Domestic

# In[16]:


def calculate_bill_from_usage_general(total_usage, afa_input):
    """Calculate electricity bill where peak usage is input as a percentage"""
    # Convert percentage to actual kWh
    energy_usage = total_usage 
    afa = total_usage * afa_input
    

    rates = TNB_DOMESTRIC_RATES['low_general'] if total_usage <= 1500 else TNB_DOMESTRIC_RATES['high_general']

    # Split usage into non-taxable (up to 600kWh) and taxable (above 600kWh)
    non_taxable_kwh = min(total_usage, 600)
    taxable_kwh = max(0, total_usage - 600)

    # Energy Efficiency Incentive (rebate is applied to total_usage)
    eei_rebate = calculate_eei_domestric(total_usage)
   
    # Distribute EEI rebate proportionally (only if applicable)
    if eei_rebate > 0:
        eei_rebate_non_tax = eei_rebate * (non_taxable_kwh / total_usage)
        eei_rebate_tax = eei_rebate * (taxable_kwh / total_usage)
    else:
        eei_rebate_non_tax = 0.0
        eei_rebate_tax = 0.0

    #AFA CALCULATION
    if afa != 0:
        afa_non_tax = afa * (non_taxable_kwh / total_usage)
        afa_tax = afa * (taxable_kwh / total_usage)
    else:
        afa_non_tax = 0.0
        afa_tax = 0.0

    
    # Charges - non-taxable part (<= 600kWh)
    nt_energy = non_taxable_kwh * rates['energy']
    nt_capacity = non_taxable_kwh * rates['capacity']
    nt_network = non_taxable_kwh * rates['network']
    nt_retail = 0  # Retail waived if total <= 600
    
    nt_net_subtotal = nt_energy + nt_capacity + nt_network + nt_retail - eei_rebate_non_tax  
    nt_subtotal = nt_net_subtotal + afa_non_tax 

    # Charges - taxable part (> 600kWh)
    t_energy = taxable_kwh * rates['energy']
    t_capacity = taxable_kwh * rates['capacity']
    t_network = taxable_kwh * rates['network']
    t_retail = rates['retail'] if total_usage > 600 else 0
    t_net_subtotal = t_energy + t_capacity + t_network + t_retail - eei_rebate_tax 
    t_subtotal = t_net_subtotal + afa_tax

    # Full subtotal before tax
    combined_net_subtotal = t_net_subtotal + nt_net_subtotal
    combined_subtotal = nt_subtotal + t_subtotal

    # Taxes
    tax_base = t_subtotal 
    service_tax = tax_base * 0.08

    # KWTBB applies only if total_usage > 300
    if total_usage > 300:
        retail_for_kwtbb = t_retail if total_usage > 600 else 0
        kwtbb = (combined_net_subtotal - retail_for_kwtbb) * 0.016
    else:
        kwtbb = 0.0

    total_bill = combined_subtotal + service_tax + kwtbb

    # Round everything to 2 decimal points
    return {
        'total_usage': round(total_usage, 2),
        'non_taxable_kwh': round(non_taxable_kwh, 2),
        'taxable_kwh': round(taxable_kwh, 2),

        'non_taxable_subtotal': round(nt_subtotal, 2),
        'taxable_subtotal': round(t_subtotal, 2),

        'energy_nt_total': round(nt_energy, 2),
        'energy_tax_total': round(t_energy, 2),
        'afa_non_tax_total': round(afa_non_tax, 2),
        'afa_tax_total': round(afa_tax, 2),
        'afa_total': round(afa, 2),
        'capacity_total': round(nt_capacity + t_capacity, 2),
        'network_total': round(nt_network + t_network, 2),
        'retail_total': round(t_retail, 2),
        'eei_rebate': round(eei_rebate, 2),
        'subtotal_before_tax': round(combined_subtotal, 2),
        'service_tax': round(service_tax, 2),
        'kwtbb': round(kwtbb, 2),
        'total_bill': round(total_bill, 2)
    }


# In[17]:


calculate_bill_from_usage_general(800,-0.0145)


# In[19]:


def reverse_tnb_general_bill(total_bill_input,afa_input,tolerance=0.01, max_kwh=10000000):
    import math

    low = 1.0
    high = max_kwh * 1.0
    guess = (low + high) / 2

    iterations = 0
    max_iterations = 100

    best_guess = None
    min_diff = float('inf')

    while iterations < max_iterations:
        result = calculate_bill_from_usage_general(guess,afa_input)
        calculated_bill = result['total_bill']
        difference = calculated_bill - total_bill_input

        if abs(difference) < min_diff:
            min_diff = abs(difference)
            best_guess = (guess, result)

        if abs(difference) <= tolerance:
            return {
                'estimated_total_kwh': round(guess, 2),
                'estimated_non_tax_kwh': round(result['non_taxable_kwh'], 2),
                'estimated_tax_kwh': round(result['taxable_kwh'], 2),
                'matched_total_bill': round(calculated_bill, 2),
                'service_tax': result['service_tax'],
                'kwtbb': result['kwtbb'],
                'retail_charge': result['retail_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'energy_non_tax_total': result['energy_nt_total'],
                'energy_tax_total': result['energy_tax_total'],
                'afa_total': result['afa_total'],
                'eei_rebate': result['eei_rebate'],
                'subtotal_before_tax': result['subtotal_before_tax'],
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
        result = calculate_bill_from_usage_general(refined_kwh,afa_input)
        calculated_bill = result['total_bill']
        diff = abs(calculated_bill - total_bill_input)
        if diff <= tolerance:
            return {
                'estimated_total_kwh': round(refined_kwh, 2),
                'estimated_non_tax_kwh': round(result['non_taxable_kwh'], 2),
                'estimated_tax_kwh': round(result['taxable_kwh'], 2),
                'matched_total_bill': round(calculated_bill, 2),
                'service_tax': result['service_tax'],
                'kwtbb': result['kwtbb'],
                'retail_charge': result['retail_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'energy_non_tax_total': result['energy_nt_total'],
                'energy_tax_total': result['energy_tax_total'],
                'afa_total': result['afa_total'],
                'eei_rebate': result['eei_rebate'],
                'subtotal_before_tax': result['subtotal_before_tax'],
                'iterations': iterations,
                'status': 'matched_in_fine_scan'
            }

    # Final fallback: return best guess even if not matched
    best_kwh = round(best_guess[0], 2)
    best_result = best_guess[1]

    return {
        'error': 'No match found within tolerance.',
        'best_guess_kwh': best_kwh,

        'estimated_non_tax_kwh': round(best_result['non_taxable_kwh'], 2),
        'estimated_tax_kwh': round(best_result['taxable_kwh'], 2),
        
        'best_matched_bill': best_result['total_bill'],
        'service_tax': best_result['service_tax'],
        'kwtbb': best_result['kwtbb'],
        'retail_charge': best_result['retail_total'],
        'network_charge': best_result['network_total'],
        'capacity_charge': best_result['capacity_total'],
        'energy_non_tax_total': best_result['energy_nt_total'],
        'energy_tax_total': best_result['energy_tax_total'], 
        'afa_total': result['afa_total'],
        'eei_rebate': best_result['eei_rebate'],
        'subtotal_before_tax': best_result['subtotal_before_tax'],
        'difference': round(abs(best_result['total_bill'] - total_bill_input), 2),
        'iterations': iterations
    }


# In[21]:


reverse_tnb_general_bill(334.05,-0.0145)


# ## DOMESTIC TOU

# In[31]:


def calculate_bill_from_usage(total_usage,peak_percent,afa_input):
    """Calculate electricity bill where peak usage is input as a percentage"""
    # Convert percentage to actual kWh
    peak_usage = total_usage * (peak_percent / 100)
    off_peak_usage = total_usage - peak_usage
    afa = total_usage * afa_input

    rates = TNB_DOMESTRIC_RATES['low_TOU'] if total_usage <= 1500 else TNB_DOMESTRIC_RATES['high_TOU']

    # Split usage into non-taxable (up to 600kWh) and taxable (above 600kWh)
    non_taxable_kwh = min(total_usage, 600)
    taxable_kwh = max(0, total_usage - 600)

    # TNB manual allocation
    non_taxable_peak = min(peak_usage, 600)
    remaining_nt = 600 - non_taxable_peak
    non_taxable_off_peak = min(off_peak_usage, remaining_nt)
    
    taxable_peak = peak_usage - non_taxable_peak
    taxable_off_peak = off_peak_usage - non_taxable_off_peak
    
    non_taxable_kwh = non_taxable_peak + non_taxable_off_peak
    taxable_kwh = taxable_peak + taxable_off_peak


    # Energy Efficiency Incentive (rebate is applied to total_usage)
    eei_rebate = calculate_eei_domestric(total_usage)
   
    # Distribute EEI rebate proportionally (only if applicable)
    if eei_rebate > 0:
        eei_rebate_non_tax = eei_rebate * (non_taxable_kwh / total_usage)
        eei_rebate_tax = eei_rebate * (taxable_kwh / total_usage)
    else:
        eei_rebate_non_tax = 0.0
        eei_rebate_tax = 0.0

    #AFA CALCULATION
    if afa != 0:
        afa_non_tax = afa * (non_taxable_kwh / total_usage)
        afa_tax = afa * (taxable_kwh / total_usage)
    else:
        afa_non_tax = 0.0
        afa_tax = 0.0

    
    # Charges - non-taxable part (<= 600kWh)
    nt_energy_peak = non_taxable_peak * rates['peak']
    nt_energy_off_peak = non_taxable_off_peak * rates['off_peak']
    nt_capacity = non_taxable_kwh * rates['capacity']
    nt_network = non_taxable_kwh * rates['network']
    nt_retail = 0  # Retail waived if total <= 600
    nt_net_subtotal = nt_energy_peak + nt_energy_off_peak + nt_capacity + nt_network + nt_retail - eei_rebate_non_tax 

    nt_subtotal = nt_net_subtotal + afa_non_tax 

    # Charges - taxable part (> 600kWh)
    t_energy_peak = taxable_peak * rates['peak']
    t_energy_off_peak = taxable_off_peak * rates['off_peak']
    t_capacity = taxable_kwh * rates['capacity']
    t_network = taxable_kwh * rates['network']
    t_retail = rates['retail'] if total_usage > 600 else 0
    t_net_subtotal = t_energy_peak + t_energy_off_peak + t_capacity + t_network + t_retail - eei_rebate_tax 
    t_subtotal = t_net_subtotal + afa_tax
  

    # Full subtotal before tax
    combined_net_subtotal = nt_net_subtotal + t_net_subtotal
    combined_subtotal = nt_subtotal + t_subtotal

    # Taxes
    tax_base = t_subtotal 
    service_tax = tax_base * 0.08

    # KWTBB applies only if total_usage > 300
    if total_usage > 300:
        retail_for_kwtbb = t_retail if total_usage > 600 else 0
        kwtbb = (combined_net_subtotal - retail_for_kwtbb) * 0.016
    else:
        kwtbb = 0.0

    total_bill = combined_subtotal + service_tax + kwtbb

    # Round everything to 2 decimal points
    return {
        'total_usage': round(total_usage, 2),
        'peak_percent': round(peak_percent, 2),
        'peak_usage_kwh': round(peak_usage, 2),
        'off_peak_usage_kwh': round(off_peak_usage, 2),

        'non_taxable_kwh': round(non_taxable_kwh, 2),
        'taxable_kwh': round(taxable_kwh, 2),

        'non_taxable_subtotal': round(nt_subtotal, 2),
        'taxable_subtotal': round(t_subtotal, 2),

        'energy_peak_total': round(nt_energy_peak + t_energy_peak, 2),
        'energy_off_peak_total': round(nt_energy_off_peak + t_energy_off_peak, 2),
        'afa_non_tax_total': round(afa_non_tax, 2),
        'afa_tax_total': round(afa_tax, 2),
        'afa_total': round(afa, 2),

        'capacity_total': round(nt_capacity + t_capacity, 2),
        'network_total': round(nt_network + t_network, 2),
        'retail_total': round(t_retail, 2),

        'eei_rebate': round(eei_rebate, 2),
        'subtotal_before_tax': round(combined_subtotal, 2),
        'service_tax': round(service_tax, 2),
        'kwtbb': round(kwtbb, 2),
        'total_bill': round(total_bill, 2)
    }


# In[32]:


def reverse_tnb_tou_bill(total_bill_input, peak_percent,afa_input,tolerance=0.01, max_kwh=5000):
    import math

    low = 1.0
    high = max_kwh * 1.0
    guess = (low + high) / 2

    iterations = 0
    max_iterations = 100

    best_guess = None
    min_diff = float('inf')

    while iterations < max_iterations:
        result = calculate_bill_from_usage(guess, peak_percent,afa_input)
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
                'service_tax': result['service_tax'],
                'kwtbb': result['kwtbb'],
                'retail_charge': result['retail_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'energy_peak_total': result['energy_peak_total'],
                'energy_off_peak_total': result['energy_off_peak_total'],
                'afa_total': result['afa_total'],
                'eei_rebate': result['eei_rebate'],
                'subtotal_before_tax': result['subtotal_before_tax'],
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
        result = calculate_bill_from_usage(refined_kwh, peak_percent,afa_input)
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
                'service_tax': result['service_tax'],
                'kwtbb': result['kwtbb'],
                'retail_charge': result['retail_total'],
                'network_charge': result['network_total'],
                'capacity_charge': result['capacity_total'],
                'energy_peak_total': result['energy_peak_total'],
                'energy_off_peak_total': result['energy_off_peak_total'],
                'afa_total': result['afa_total'],
                'eei_rebate': result['eei_rebate'],
                'subtotal_before_tax': result['subtotal_before_tax'],
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
        'service_tax': best_result['service_tax'],
        'kwtbb': best_result['kwtbb'],
        'retail_charge': best_result['retail_total'],
        'network_charge': best_result['network_total'],
        'capacity_charge': best_result['capacity_total'],
        'energy_peak_total': best_result['energy_peak_total'],
        'energy_off_peak_total': best_result['energy_off_peak_total'],
        'afa_total': best_result['afa_total'],
        'eei_rebate': best_result['eei_rebate'],
        'subtotal_before_tax': best_result['subtotal_before_tax'],
        'difference': round(abs(best_result['total_bill'] - total_bill_input), 2),
        'iterations': iterations
    }


# In[33]:


calculate_bill_from_usage(1200, 25,-0.0145)


# In[36]:


# Say user inputs:

total_paid = 535.24
peak_usage_percent = 25

estimate = reverse_tnb_tou_bill(total_paid, peak_usage_percent,-0.0145)
print(estimate)


# In[ ]:





# In[ ]:





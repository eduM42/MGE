import numpy as np

def calculate_rms(values):
    arr = np.array(values)
    return float(np.sqrt(np.mean(np.square(arr))))

def calculate_power(voltage_rms, current_rms):
    return float(voltage_rms * current_rms)

def calculate_power_factor(voltage_values, current_values):
    v = np.array(voltage_values) - np.mean(voltage_values)
    i = np.array(current_values) - np.mean(current_values)
    correlation = np.correlate(v, i, mode='full')
    delay = correlation.argmax() - (len(v) - 1)
    # Assume 60Hz, 500 samples per packet
    period = 1/60
    sample_interval = period / len(v)
    phase_diff = 2 * np.pi * delay * sample_interval / period
    pf = float(np.cos(phase_diff))
    return pf

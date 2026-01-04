
import numpy as np
import skfuzzy as fuzz

# Universe of Discourse
# Temperature: 0 to 50 Celsius
TEMP_RANGE = np.arange(0, 51, 1)
# Humidity: 0 to 100 Percent
HUMIDITY_RANGE = np.arange(0, 101, 1)
# Growth Stage: 0 to 100 (Day/Index)
GROWTH_RANGE = np.arange(0, 101, 1)

# Outputs
# Heater/Fan: -100 (Full Cooling) to 100 (Full Heating)
# This combined output approach simplifies the rule base significantly.
# Negative values = Fan/Cooling, Positive values = Heater.
TEMP_CONTROL_RANGE = np.arange(-100, 101, 1)

# Misting: 0 to 100%
MISTING_RANGE = np.arange(0, 101, 1)

def generate_membership_functions(range_array, labels=['Very Low', 'Low', 'Ideal', 'High', 'Very High']):
    """
    Generates standard triangular membership functions for a given range.
    For 5 sets, we can distribute them evenly initially.
    """
    funcs = {}
    step = (range_array.max() - range_array.min()) / (len(labels) - 1)
    
    for i, label in enumerate(labels):
        center = range_array.min() + i * step
        # Triangle shape: starts at center-step, peaks at center, ends at center+step
        # Basic implementation, can be optimized later
        if i == 0:
             # Left shoulder
             funcs[label] = fuzz.trimf(range_array, [range_array.min(), range_array.min(), range_array.min() + step])
        elif i == len(labels) - 1:
            # Right shoulder
             funcs[label] = fuzz.trimf(range_array, [range_array.max() - step, range_array.max(), range_array.max()])
        else:
            funcs[label] = fuzz.trimf(range_array, [center - step, center, center + step])
            
    return funcs

# Initial standard membership functions (will be optimized later)
temp_mfs = generate_membership_functions(TEMP_RANGE)
humidity_mfs = generate_membership_functions(HUMIDITY_RANGE)
growth_mfs = generate_membership_functions(GROWTH_RANGE)

# Output MFs usually remain static or are also optimized. For Mamdani they are fuzzy sets.
temp_control_mfs = generate_membership_functions(TEMP_CONTROL_RANGE, labels=['Cooling_Strong', 'Cooling_Weak', 'Off', 'Heating_Weak', 'Heating_Strong'])
misting_mfs = generate_membership_functions(MISTING_RANGE, labels=['Off', 'Low', 'Medium', 'High', 'Max'])

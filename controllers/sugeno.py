
import numpy as np
import skfuzzy as fuzz
from model.variables import TEMP_RANGE, HUMIDITY_RANGE, GROWTH_RANGE, generate_membership_functions

class SugenoController:
    def __init__(self):
        # We need the same MFs for inputs to calculate firing strength
        self.temp_mfs = generate_membership_functions(TEMP_RANGE)
        self.humidity_mfs = generate_membership_functions(HUMIDITY_RANGE)
        self.growth_mfs = generate_membership_functions(GROWTH_RANGE)
        
        # Singleton Constants for Sugeno Outputs (0th order)
        # Heater/Fan
        self.output_hf = {
            'Cooling_Strong': -100,
            'Cooling_Weak': -50,
            'Off': 0,
            'Heating_Weak': 50,
            'Heating_Strong': 100
        }
        
        # Misting
        self.output_mist = {
            'Off': 0,
            'Low': 25,
            'Medium': 50,
            'High': 75,
            'Max': 100
        }

    def _get_membership(self, value, mfs):
        """Calculates membership degree for a specific value against all MFs."""
        memberships = {}
        for label, mf in mfs.items():
            memberships[label] = fuzz.interp_membership(np.arange(0, len(mf)), mf, value) 
            # Note: The fuzz.interp_membership expects the x-range of the MF. 
            # Our calculate_membership logic needs the original x range used to create the MF.
            # We implemented generate_membership_functions using specific ranges.
            # Let's direct access:
            
        return memberships
        
    def compute(self, temp, humidity, growth):
        """
        Manually evaluates the 25 rules.
        """
        
        # 1. Fuzzification
        # We need to pass the correct ranges.
        t_mu = {l: fuzz.interp_membership(TEMP_RANGE, mf, temp) for l, mf in self.temp_mfs.items()}
        h_mu = {l: fuzz.interp_membership(HUMIDITY_RANGE, mf, humidity) for l, mf in self.humidity_mfs.items()}
        g_mu = {l: fuzz.interp_membership(GROWTH_RANGE, mf, growth) for l, mf in self.growth_mfs.items()}
        
        rules = []
        
        # Helper to add rule (Antecedent strength, HF Output Constant, Mist Output Constant)
        def add_rule(strength, hf_label, mist_label):
            rules.append((strength, self.output_hf[hf_label], self.output_mist[mist_label]))

        # Re-implementing the 25 rules logic from rules.py but for manual calculation
        # AND operator = np.fmin (or min)
        
        # 1. Extreme Heat & Dryness
        add_rule(min(t_mu['Very High'], h_mu['Very Low']), 'Cooling_Strong', 'Max')
        add_rule(min(t_mu['Very High'], h_mu['Low']), 'Cooling_Strong', 'High')
        add_rule(min(t_mu['High'], h_mu['Very Low']), 'Cooling_Strong', 'High')
        
        # 2. Extreme Cold & Wet
        add_rule(min(t_mu['Very Low'], h_mu['Very High']), 'Heating_Strong', 'Off')
        add_rule(min(t_mu['Very Low'], h_mu['High']), 'Heating_Strong', 'Off')
        
        # 3. Ideal
        add_rule(min(t_mu['Ideal'], h_mu['Ideal']), 'Off', 'Off')
        
        # 4. High Temp, Ideal Humidity
        add_rule(min(t_mu['High'], h_mu['Ideal']), 'Cooling_Weak', 'Low')
        
        # 5. Low Temp, Ideal Humidity
        add_rule(min(t_mu['Low'], h_mu['Ideal']), 'Heating_Weak', 'Off')
        
        # 6. Growth Stage Specifics
        add_rule(min(g_mu['Very Low'], t_mu['Low']), 'Heating_Weak', 'Off')
        add_rule(min(g_mu['Very Low'], t_mu['High']), 'Cooling_Weak', 'Low')
        
        # 7. Mature Plants
        add_rule(min(g_mu['Very High'], t_mu['High'], h_mu['Low']), 'Cooling_Weak', 'Medium')
        
        # 8. Handling Humidity Specifics
        add_rule(min(h_mu['Very Low'], t_mu['Ideal']), 'Off', 'High')
        add_rule(min(h_mu['Low'], t_mu['Ideal']), 'Off', 'Medium')
        add_rule(min(h_mu['High'], t_mu['Ideal']), 'Cooling_Weak', 'Off')
        add_rule(min(h_mu['Very High'], t_mu['Ideal']), 'Cooling_Strong', 'Off')
        
        # 9. Mixed
        add_rule(min(t_mu['High'], h_mu['High']), 'Cooling_Strong', 'Off')
        add_rule(min(t_mu['Low'], h_mu['Low']), 'Heating_Weak', 'Medium')
        
        # 10. 'Very Low' Temp
        add_rule(min(t_mu['Very Low'], h_mu['Ideal']), 'Heating_Strong', 'Off')
        add_rule(min(t_mu['Very Low'], h_mu['Low']), 'Heating_Strong', 'Low')
        add_rule(min(t_mu['Very Low'], h_mu['Very Low']), 'Heating_Strong', 'Medium')
        
        # 11. 'Very High' Temp
        add_rule(min(t_mu['Very High'], h_mu['Ideal']), 'Cooling_Strong', 'Medium')
        add_rule(min(t_mu['Very High'], h_mu['High']), 'Cooling_Strong', 'Low')
        add_rule(min(t_mu['Very High'], h_mu['Very High']), 'Cooling_Strong', 'Off')
        
        # 12. Transitions
        add_rule(min(g_mu['Low'], t_mu['High'], h_mu['Low']), 'Cooling_Weak', 'Medium')
        add_rule(min(g_mu['High'], t_mu['Low'], h_mu['High']), 'Heating_Weak', 'Off')

        # Defuzzification (Weighted Average)
        numerator_hf = 0
        denominator_hf = 0
        numerator_mist = 0
        denominator_mist = 0
        
        for strength, hf_val, mist_val in rules:
            numerator_hf += strength * hf_val
            denominator_hf += strength
            
            numerator_mist += strength * mist_val
            denominator_mist += strength
            
        # Avoid division by zero
        out_hf = numerator_hf / denominator_hf if denominator_hf > 0 else 0
        out_mist = numerator_mist / denominator_mist if denominator_mist > 0 else 0
        
        return {
            'heater_fan': out_hf,
            'misting': out_mist
        }

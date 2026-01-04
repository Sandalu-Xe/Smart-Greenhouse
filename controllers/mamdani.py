
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from model.variables import TEMP_RANGE, HUMIDITY_RANGE, GROWTH_RANGE, TEMP_CONTROL_RANGE, MISTING_RANGE, generate_membership_functions
from controllers.rules import define_rules

class MamdaniController:
    def __init__(self):
        # Antecedents
        self.temp = ctrl.Antecedent(TEMP_RANGE, 'temp')
        self.humidity = ctrl.Antecedent(HUMIDITY_RANGE, 'humidity')
        self.growth_stage = ctrl.Antecedent(GROWTH_RANGE, 'growth_stage')
        
        # Consequents
        self.heater_fan = ctrl.Consequent(TEMP_CONTROL_RANGE, 'heater_fan')
        self.misting = ctrl.Consequent(MISTING_RANGE, 'misting')
        
        # Determine membership functions (Initial Default)
        # We re-generate them here or load them. For now, re-generating to ensure they are attached to the Antecedent objects appropriately if needed, 
        # though skfuzzy usually wants them assigned to the .automf() or .universe. 
        # We will use the custom dictionary we made in variables.py but apply them to the skfuzzy objects.
        
        self._apply_membership_functions(self.temp, TEMP_RANGE)
        self._apply_membership_functions(self.humidity, HUMIDITY_RANGE)
        self._apply_membership_functions(self.growth_stage, GROWTH_RANGE)
        
        self._apply_membership_functions(self.heater_fan, TEMP_CONTROL_RANGE, labels=['Cooling_Strong', 'Cooling_Weak', 'Off', 'Heating_Weak', 'Heating_Strong'])
        self._apply_membership_functions(self.misting, MISTING_RANGE, labels=['Off', 'Low', 'Medium', 'High', 'Max'])
        
        # Rules
        self.rules = define_rules(self.temp, self.humidity, self.growth_stage, self.heater_fan, self.misting)
        
        # Control System
        self.ctrl_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.ctrl_system)
        
    def _apply_membership_functions(self, fuzzy_var, range_array, labels=['Very Low', 'Low', 'Ideal', 'High', 'Very High']):
        mfs = generate_membership_functions(range_array, labels)
        for label, mf in mfs.items():
            fuzzy_var[label] = mf

    def compute(self, temp_input, humidity_input, growth_input):
        self.simulation.input['temp'] = temp_input
        self.simulation.input['humidity'] = humidity_input
        self.simulation.input['growth_stage'] = growth_input
        
        try:
            self.simulation.compute()
            return {
                'heater_fan': self.simulation.output['heater_fan'],
                'misting': self.simulation.output['misting']
            }
        except Exception as e:
            # Fallback if rule not fired (though we have defaults/should ideally cover space)
            print(f"Warning: No rule fired for inputs {temp_input}, {humidity_input}, {growth_input}. Error: {e}")
            return {'heater_fan': 0, 'misting': 0}
            
    def update_membership_functions(self, variable_name, new_params):
        """
        Method to update MFs during optimization. 
        new_params would be a dictionary of label -> [a, b, c] for trimf.
        """
        # This requires re-initializing the system usually in skfuzzy or modifying the underlying terms.
        # For simplicity in this demo, we might just assume fixed MFs for the first pass.
        pass

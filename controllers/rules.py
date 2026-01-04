
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def define_rules(temp, humidity, growth_stage, heater_fan, misting):
    """
    Defines 25 fuzzy rules based on the 3 inputs and 2 outputs.
    
    Inputs:
    - temp: Temperature Antecedent
    - humidity: Humidity Antecedent
    - growth_stage: Growth Stage Antecedent
    
    Outputs:
    - heater_fan: Heater/Fan Consequent
    - misting: Misting Consequent
    
    Labels: 'Very Low', 'Low', 'Ideal', 'High', 'Very High'
    Output Labels (Heater/Fan): 'Cooling_Strong', 'Cooling_Weak', 'Off', 'Heating_Weak', 'Heating_Strong'
    Output Labels (Misting): 'Off', 'Low', 'Medium', 'High', 'Max'
    """
    
    # Define mapping for easier rule creation if needed, but we will write them out explicitly to ensure 25.
    
    rules = []
    
    # 1. Extreme Heat & Dryness (Critical for all)
    rules.append(ctrl.Rule(temp['Very High'] & humidity['Very Low'], (heater_fan['Cooling_Strong'], misting['Max'])))
    rules.append(ctrl.Rule(temp['Very High'] & humidity['Low'], (heater_fan['Cooling_Strong'], misting['High'])))
    rules.append(ctrl.Rule(temp['High'] & humidity['Very Low'], (heater_fan['Cooling_Strong'], misting['High'])))
    
    # 2. Extreme Cold & Wet (Risk of mold/freezing)
    rules.append(ctrl.Rule(temp['Very Low'] & humidity['Very High'], (heater_fan['Heating_Strong'], misting['Off'])))
    rules.append(ctrl.Rule(temp['Very Low'] & humidity['High'], (heater_fan['Heating_Strong'], misting['Off'])))
    
    # 3. Ideal Conditions (Maintain)
    rules.append(ctrl.Rule(temp['Ideal'] & humidity['Ideal'], (heater_fan['Off'], misting['Off'])))
    
    # 4. High Temp, Ideal Humidity
    rules.append(ctrl.Rule(temp['High'] & humidity['Ideal'], (heater_fan['Cooling_Weak'], misting['Low'])))
    
    # 5. Low Temp, Ideal Humidity
    rules.append(ctrl.Rule(temp['Low'] & humidity['Ideal'], (heater_fan['Heating_Weak'], misting['Off'])))
    
    # 6. Growth Stage Specifics: Seedling (Very Low Stage) needs stable warmth and humidity
    rules.append(ctrl.Rule(growth_stage['Very Low'] & temp['Low'], (heater_fan['Heating_Weak'], misting['Off'])))
    rules.append(ctrl.Rule(growth_stage['Very Low'] & temp['High'], (heater_fan['Cooling_Weak'], misting['Low'])))
    
    # 7. Mature Plants (Very High Stage) can tolerate more, but need resource optimization
    rules.append(ctrl.Rule(growth_stage['Very High'] & temp['High'] & humidity['Low'], (heater_fan['Cooling_Weak'], misting['Medium'])))
    
    # 8. Handling Humidity Specifics
    rules.append(ctrl.Rule(humidity['Very Low'] & temp['Ideal'], (heater_fan['Off'], misting['High'])))
    rules.append(ctrl.Rule(humidity['Low'] & temp['Ideal'], (heater_fan['Off'], misting['Medium'])))
    rules.append(ctrl.Rule(humidity['High'] & temp['Ideal'], (heater_fan['Cooling_Weak'], misting['Off']))) # Fan helps reduce humidity
    rules.append(ctrl.Rule(humidity['Very High'] & temp['Ideal'], (heater_fan['Cooling_Strong'], misting['Off'])))
    
    # 9. Mixed Conditions (Temp & Humidity conflicts)
    rules.append(ctrl.Rule(temp['High'] & humidity['High'], (heater_fan['Cooling_Strong'], misting['Off']))) # Hot and Muggy -> Cool hard, no mist
    rules.append(ctrl.Rule(temp['Low'] & humidity['Low'], (heater_fan['Heating_Weak'], misting['Medium']))) # Cold and Dry -> Heat, add moisture
    
    # 10. Rules for 'Very Low' Temp (Freezing risk)
    rules.append(ctrl.Rule(temp['Very Low'] & humidity['Ideal'], (heater_fan['Heating_Strong'], misting['Off'])))
    rules.append(ctrl.Rule(temp['Very Low'] & humidity['Low'], (heater_fan['Heating_Strong'], misting['Low'])))
    rules.append(ctrl.Rule(temp['Very Low'] & humidity['Very Low'], (heater_fan['Heating_Strong'], misting['Medium']))) # Don't mist too much when freezing
    
    # 11. Rules for 'Very High' Temp with varying humidity
    rules.append(ctrl.Rule(temp['Very High'] & humidity['Ideal'], (heater_fan['Cooling_Strong'], misting['Medium'])))
    rules.append(ctrl.Rule(temp['Very High'] & humidity['High'], (heater_fan['Cooling_Strong'], misting['Low']))) # Evaporative cooling less effective
    rules.append(ctrl.Rule(temp['Very High'] & humidity['Very High'], (heater_fan['Cooling_Strong'], misting['Off']))) # Sauna condition -> Just Fan
    
    # 12. Transition Rules (Low/High Stage with suboptimal conditions)
    rules.append(ctrl.Rule(growth_stage['Low'] & temp['High'] & humidity['Low'], (heater_fan['Cooling_Weak'], misting['Medium'])))
    rules.append(ctrl.Rule(growth_stage['High'] & temp['Low'] & humidity['High'], (heater_fan['Heating_Weak'], misting['Off'])))
    
    return rules


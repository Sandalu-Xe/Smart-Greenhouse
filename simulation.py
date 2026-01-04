
import numpy as np
import time
from model.plants import ALL_PLANTS

class GreenhouseSimulation:
    def __init__(self, mamdani_ctrl, sugeno_ctrl):
        self.mamdani = mamdani_ctrl
        self.sugeno = sugeno_ctrl
        self.results = []

    def run_random_tests(self, num_tests=20, steps_per_test=50):
        print(f"Running {num_tests} random simulation tests...")
        
        metrics = {
            'Mamdani': {'avg_response': 0, 'avg_error': 0, 'avg_energy': 0, 'avg_smoothness': 0},
            'Sugeno': {'avg_response': 0, 'avg_error': 0, 'avg_energy': 0, 'avg_smoothness': 0}
        }
        
        for i in range(num_tests):
            # Random Plant Selection
            plant = ALL_PLANTS[np.random.randint(0, len(ALL_PLANTS))]
            
            # Random Initial Conditions
            # Start somewhere reasonable but off-target
            curr_temp = np.random.uniform(5, 45)
            curr_hum = np.random.uniform(10, 90)
            curr_growth = np.random.uniform(0, 100)
            
            # Run per controller
            for ctrl_name, controller in [('Mamdani', self.mamdani), ('Sugeno', self.sugeno)]:
                
                sim_error = 0
                sim_energy = 0
                sim_smoothness = 0
                total_time = 0
                
                prev_outputs = [0, 0] # hf, mist
                outputs_history = []
                
                # Temp simulation state variables (reset for each controller to compare fairly)
                sim_temp = curr_temp
                sim_hum = curr_hum
                
                for step in range(steps_per_test):
                    start_time = time.time()
                    
                    # Compute Control Action
                    # For Mamdani using skfuzzy simulation
                    # For Sugeno using manual compute
                    if ctrl_name == 'Mamdani':
                        res = controller.compute(sim_temp, sim_hum, curr_growth)
                    else:
                        res = controller.compute(sim_temp, sim_hum, curr_growth)
                        
                    end_time = time.time()
                    total_time += (end_time - start_time)
                    
                    hf_out = res['heater_fan']
                    mist_out = res['misting']
                    
                    # Physics approximation (Simple Plant Model)
                    # Heater increases temp, Fan decreases temp & humidity, Misting increases humidity & slight cooling
                    # This is just for "closed loop" simulation feel
                    
                    # 1 unit of Heat = +0.5 deg C
                    # 1 unit of Cool = -0.5 deg C
                    # 1 unit of Mist = +1 % Hum, -0.1 deg C
                    
                    # Apply physics
                    temp_change = 0
                    hum_change = 0
                    
                    if hf_out > 0: # Heating
                         temp_change += (hf_out / 100.0) * 0.5
                    else: # Cooling
                         temp_change += (hf_out / 100.0) * 0.5 # hf_out is negative
                         hum_change += (hf_out / 100.0) * 0.2 # Fan dries slightly
                         
                    if mist_out > 0:
                        hum_change += (mist_out / 100.0) * 1.0
                        temp_change -= (mist_out / 100.0) * 0.1
                        
                    sim_temp += temp_change
                    sim_hum += hum_change
                    
                    # Natural decay towards ambient (say 25C, 50%)
                    sim_temp += (25 - sim_temp) * 0.05
                    sim_hum += (50 - sim_hum) * 0.05
                    
                    # Clip
                    sim_temp = np.clip(sim_temp, 0, 50)
                    sim_hum = np.clip(sim_hum, 0, 100)
                    
                    # Metrics Calculation
                    # Error: Distance from ideal
                    err = np.sqrt((sim_temp - plant.ideal_temp)**2 + (sim_hum - plant.ideal_humidity)**2)
                    sim_error += err
                    
                    # Energy: Absolute control effort
                    sim_energy += abs(hf_out) + abs(mist_out)
                    
                    # Smoothness: Change in output
                    smooth = abs(hf_out - prev_outputs[0]) + abs(mist_out - prev_outputs[1])
                    sim_smoothness += smooth
                    
                    prev_outputs = [hf_out, mist_out]
                    
                # Store test average
                metrics[ctrl_name]['avg_response'] += (total_time / steps_per_test)
                metrics[ctrl_name]['avg_error'] += (sim_error / steps_per_test)
                metrics[ctrl_name]['avg_energy'] += (sim_energy / steps_per_test)
                metrics[ctrl_name]['avg_smoothness'] += (sim_smoothness / steps_per_test)

        # Average over all tests
        for key in metrics:
            for m in metrics[key]:
                metrics[key][m] /= num_tests
                
        return metrics

    def generate_report(self, metrics):
        print("\n" + "="*50)
        print("PERFORMANCE COMPARISON REPORT")
        print("="*50)
        print(f"{'Controller':<15} | {'Resp Time (ms)':<15} | {'Avg Error':<10} | {'Energy':<10} | {'Smoothness':<10}")
        print("-" * 70)
        
        m = metrics['Mamdani']
        print(f"{'Mamdani':<15} | {m['avg_response']*1000:<15.4f} | {m['avg_error']:<10.2f} | {m['avg_energy']:<10.2f} | {m['avg_smoothness']:<10.2f}")
        
        s = metrics['Sugeno']
        print(f"{'Sugeno':<15} | {s['avg_response']*1000:<15.4f} | {s['avg_error']:<10.2f} | {s['avg_energy']:<10.2f} | {s['avg_smoothness']:<10.2f}")
        print("-" * 70)

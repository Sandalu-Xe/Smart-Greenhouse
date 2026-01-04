
import sys
from controllers.mamdani import MamdaniController
from controllers.sugeno import SugenoController
from simulation import GreenhouseSimulation
from optimization.optimizer import GeneticOptimizer

def main():
    print("Initializing Smart Greenhouse Control System...")
    
    # 1. Initialize Controllers
    print("Initializing Mamdani Controller...")
    mamdani = MamdaniController()
    print("Initializing Sugeno Controller...")
    sugeno = SugenoController()
    
    # 2. Optimization (Optional but requested)
    print("\n[Optional] Running Genetic Algorithm Optimization for Sugeno MFs...")
    # Creates a simulation runner for the optimizer
    sim_for_opt = GreenhouseSimulation(mamdani, sugeno)
    optimizer = GeneticOptimizer(sim_for_opt, population_size=5, generations=3) # Small for speed in demo
    best_factor = optimizer.run()
    
    # Apply optimization results (Conceptual step for this demo)
    print(f"Optimization finished. Optimized Factor: {best_factor}")
    
    # 3. Final Performance Comparison
    print("\nRunning Final Performance Comparison (20 Random Tests)...")
    sim_final = GreenhouseSimulation(mamdani, sugeno)
    metrics = sim_final.run_random_tests(num_tests=20, steps_per_test=50)
    
    # 4. Generate Report
    sim_final.generate_report(metrics)

if __name__ == "__main__":
    main()

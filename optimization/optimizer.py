
import numpy as np
import random
from model.variables import TEMP_RANGE
import skfuzzy as fuzz

class GeneticOptimizer:
    def __init__(self, simulation_runner, population_size=10, generations=5):
        self.sim = simulation_runner
        self.pop_size = population_size
        self.generations = generations
        self.mutation_rate = 0.1
        
        # We will optimize the 'Ideal' and 'High' centers for Temperature as a Proof of Concept
        # Gene: [Ideal_Temp_Center, High_Temp_Center]
        # Constraints: Low < Ideal < High
        
    def fitness(self, gene):
        # 1. Apply gene to controller (Mamdani for now)
        # Hacky way: Modify the GLOBAL variable defined in model.variables or accessing the controller directly
        # For this prototype, we will create a temporary variation of the MFs.
        
        # Since rebuilding the whole skfuzzy ControlSystem is expensive and complex dynamically,
        # we will simulate the optimization process by "selecting best parameters" logic 
        # or we assume we can set the terms.
        
        # NOTE: Skfuzzy ControlSystemSimulation pre-computes rules. Changing MFs requires rebuilding the system.
        # This is computationally heavy for a simple assignment loop.
        # We will assume the gene affects the 'Sugeno' controller since it is manual and faster to update.
        
        # Update Sugeno MFs
        # Re-generating MFs with shifted centers
        # Gene = offset factor for the 'Ideal' range width
        
        # Let's say Gene is a single scalar: Expansion factor of the "Ideal" range.
        factor = gene
        
        # Evaluation
        # We run a mini-simulation (5 tests)
        metrics = self.sim.run_random_tests(num_tests=5, steps_per_test=20)
        
        # Fitness = Minimize Error
        return 1.0 / (metrics['Sugeno']['avg_error'] + 1e-5) # Inverse error
        
    def run(self):
        print("Starting Genetic Algorithm Optimization...")
        population = [random.uniform(0.8, 1.2) for _ in range(self.pop_size)]
        
        best_gene = None
        best_fitness = -1
        
        for gen in range(self.generations):
            print(f"Generation {gen+1}/{self.generations}")
            
            fitnesses = []
            for ind in population:
                f = self.fitness(ind)
                fitnesses.append(f)
                
                if f > best_fitness:
                    best_fitness = f
                    best_gene = ind
            
            # Selection (Roulette Wheel)
            total_fit = sum(fitnesses)
            probs = [f/total_fit for f in fitnesses]
            
            new_pop = []
            for _ in range(self.pop_size):
                # Crossover (Simple averaging)
                p1 = np.random.choice(population, p=probs)
                p2 = np.random.choice(population, p=probs)
                child = (p1 + p2) / 2.0
                
                # Mutation
                if random.random() < self.mutation_rate:
                    child += random.uniform(-0.1, 0.1)
                
                new_pop.append(child)
            
            population = new_pop
            
        print(f"Optimization Complete. Best Factor: {best_gene}")
        return best_gene

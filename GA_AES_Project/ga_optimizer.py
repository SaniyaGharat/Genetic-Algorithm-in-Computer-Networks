"""
Genetic Algorithm for AES Key Schedule Optimization
Optimizes rotation values and Rcon multipliers to improve security and performance
"""

import numpy as np
import random
from Crypto.Random import get_random_bytes
import copy
import time


class KeyScheduleChromosome:
    """
    Represents a key schedule configuration as a chromosome
    Genes: rotation values (1-3) and rcon multipliers (1-3) for 10 rounds
    """
    
    def __init__(self, rotations=None, rcon_multipliers=None):
        if rotations is None:
            # Random initialization: rotations between 1-3
            self.rotations = [random.randint(1, 3) for _ in range(10)]
        else:
            self.rotations = rotations
        
        if rcon_multipliers is None:
            # Random initialization: multipliers between 1-3
            self.rcon_multipliers = [random.randint(1, 3) for _ in range(10)]
        else:
            self.rcon_multipliers = rcon_multipliers
        
        self.fitness = 0.0
        self.metrics = {}
    
    def to_params(self):
        """Convert chromosome to key schedule parameters"""
        return {
            'rotations': self.rotations,
            'rcon_multipliers': self.rcon_multipliers
        }
    
    def __repr__(self):
        return f"Chromosome(fitness={self.fitness:.4f}, rot={self.rotations}, rcon={self.rcon_multipliers})"


class GeneticAlgorithm:
    """
    Genetic Algorithm for optimizing AES key schedule
    """
    
    def __init__(self, 
                 custom_aes_class,
                 security_metrics_class,
                 population_size=25,
                 crossover_rate=0.8,
                 mutation_rate=0.2,
                 num_generations=30,
                 elitism_count=2):
        
        self.CustomAES = custom_aes_class
        self.SecurityMetrics = security_metrics_class
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.num_generations = num_generations
        self.elitism_count = elitism_count
        
        # Evolution tracking
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.best_chromosome = None
        
        # Test key for consistency
        self.test_key = get_random_bytes(16)
        
        # Weights for fitness function
        self.w_avalanche = 0.4  # Avalanche effect weight
        self.w_entropy = 0.3    # Key schedule entropy weight
        self.w_speed = 0.3      # Encryption speed weight
    
    def initialize_population(self):
        """Create initial random population"""
        population = []
        
        # Add standard AES as baseline
        standard = KeyScheduleChromosome(
            rotations=[1]*10,
            rcon_multipliers=[1]*10
        )
        population.append(standard)
        
        # Random chromosomes
        for _ in range(self.population_size - 1):
            chromosome = KeyScheduleChromosome()
            population.append(chromosome)
        
        return population
    
    def evaluate_fitness(self, chromosome):
        """
        Evaluate chromosome fitness based on:
        1. Avalanche effect (closer to 50% is better)
        2. Key schedule entropy (higher is better)
        3. Encryption speed (faster is better)
        """
        # Create AES instance with this chromosome's parameters
        aes = self.CustomAES(chromosome.to_params())
        metrics = self.SecurityMetrics()
        
        # Measure avalanche effect
        avalanche_mean, avalanche_std = metrics.calculate_avalanche_effect(
            aes, self.test_key, num_tests=50
        )
        
        # Measure encryption time
        enc_time = metrics.measure_encryption_time(
            aes, self.test_key, data_size=512, iterations=50
        )
        
        # Calculate key schedule entropy
        _ = aes.encrypt(b"test" * 4, self.test_key)  # Trigger key expansion
        entropy = aes.get_key_schedule_entropy()
        
        # Normalize metrics to [0, 1] range
        # Avalanche: ideal is 50%, normalize deviation from 50
        avalanche_score = 1.0 - abs(avalanche_mean - 50.0) / 50.0
        avalanche_score = max(0, avalanche_score)
        
        # Entropy: normalize to [0, 1] (max entropy is 8 bits for bytes)
        entropy_score = entropy / 8.0
        
        # Speed: normalize inversely (faster is better)
        # Typical range: 0.01 - 0.1 ms, invert and normalize
        speed_score = 1.0 / (1.0 + enc_time * 10)  # Scale to reasonable range
        
        # Calculate weighted fitness
        fitness = (self.w_avalanche * avalanche_score +
                   self.w_entropy * entropy_score +
                   self.w_speed * speed_score)
        
        # Store metrics for analysis
        chromosome.metrics = {
            'avalanche_mean': avalanche_mean,
            'avalanche_std': avalanche_std,
            'encryption_time': enc_time,
            'entropy': entropy,
            'avalanche_score': avalanche_score,
            'entropy_score': entropy_score,
            'speed_score': speed_score
        }
        
        return fitness
    
    def selection_tournament(self, population, tournament_size=3):
        """Select parent using tournament selection"""
        tournament = random.sample(population, tournament_size)
        winner = max(tournament, key=lambda x: x.fitness)
        return winner
    
    def crossover_single_point(self, parent1, parent2):
        """Single-point crossover for two parents"""
        if random.random() > self.crossover_rate:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        # Crossover point
        point = random.randint(1, 9)
        
        # Create offspring
        child1_rot = parent1.rotations[:point] + parent2.rotations[point:]
        child1_rcon = parent1.rcon_multipliers[:point] + parent2.rcon_multipliers[point:]
        
        child2_rot = parent2.rotations[:point] + parent1.rotations[point:]
        child2_rcon = parent2.rcon_multipliers[:point] + parent1.rcon_multipliers[point:]
        
        child1 = KeyScheduleChromosome(child1_rot, child1_rcon)
        child2 = KeyScheduleChromosome(child2_rot, child2_rcon)
        
        return child1, child2
    
    def mutate(self, chromosome):
        """Randomly mutate chromosome genes"""
        # Mutate rotations
        for i in range(len(chromosome.rotations)):
            if random.random() < self.mutation_rate:
                chromosome.rotations[i] = random.randint(1, 3)
        
        # Mutate rcon multipliers
        for i in range(len(chromosome.rcon_multipliers)):
            if random.random() < self.mutation_rate:
                chromosome.rcon_multipliers[i] = random.randint(1, 3)
        
        return chromosome
    
    def evolve(self):
        """Run the genetic algorithm"""
        print(f"Starting GA with population={self.population_size}, generations={self.num_generations}")
        print(f"Crossover rate={self.crossover_rate}, Mutation rate={self.mutation_rate}\n")
        
        # Initialize population
        population = self.initialize_population()
        
        # Evaluate initial population
        print("Evaluating initial population...")
        for chromosome in population:
            chromosome.fitness = self.evaluate_fitness(chromosome)
        
        # Evolution loop
        for generation in range(self.num_generations):
            start_time = time.time()
            
            # Sort by fitness
            population.sort(key=lambda x: x.fitness, reverse=True)
            
            # Track statistics
            best_fitness = population[0].fitness
            avg_fitness = np.mean([c.fitness for c in population])
            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            
            print(f"Generation {generation+1}/{self.num_generations} | "
                  f"Best Fitness: {best_fitness:.4f} | "
                  f"Avg Fitness: {avg_fitness:.4f} | "
                  f"Time: {time.time()-start_time:.2f}s")
            
            # Store best chromosome
            if self.best_chromosome is None or best_fitness > self.best_chromosome.fitness:
                self.best_chromosome = copy.deepcopy(population[0])
            
            # Create next generation
            next_generation = []
            
            # Elitism: keep best chromosomes
            next_generation.extend(copy.deepcopy(c) for c in population[:self.elitism_count])
            
            # Generate offspring
            while len(next_generation) < self.population_size:
                # Selection
                parent1 = self.selection_tournament(population)
                parent2 = self.selection_tournament(population)
                
                # Crossover
                child1, child2 = self.crossover_single_point(parent1, parent2)
                
                # Mutation
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                # Add to next generation
                next_generation.append(child1)
                if len(next_generation) < self.population_size:
                    next_generation.append(child2)
            
            # Evaluate new generation
            for chromosome in next_generation[self.elitism_count:]:
                chromosome.fitness = self.evaluate_fitness(chromosome)
            
            population = next_generation
        
        # Final evaluation
        population.sort(key=lambda x: x.fitness, reverse=True)
        self.best_chromosome = population[0]
        
        print(f"\n=== Evolution Complete ===")
        print(f"Best Fitness: {self.best_chromosome.fitness:.4f}")
        print(f"Best Rotations: {self.best_chromosome.rotations}")
        print(f"Best Rcon Multipliers: {self.best_chromosome.rcon_multipliers}")
        print(f"\nBest Chromosome Metrics:")
        for key, value in self.best_chromosome.metrics.items():
            print(f"  {key}: {value}")
        
        return self.best_chromosome
    
    def get_evolution_history(self):
        """Return fitness history for plotting"""
        return {
            'generations': list(range(1, len(self.best_fitness_history) + 1)),
            'best_fitness': self.best_fitness_history,
            'avg_fitness': self.avg_fitness_history
        }


# Example usage
if __name__ == "__main__":
    from aes_custom import CustomAES, SecurityMetrics
    
    # Create GA instance
    ga = GeneticAlgorithm(
        custom_aes_class=CustomAES,
        security_metrics_class=SecurityMetrics,
        population_size=20,
        crossover_rate=0.8,
        mutation_rate=0.2,
        num_generations=15,  # Reduced for quick testing
        elitism_count=2
    )
    
    # Run evolution
    best_chromosome = ga.evolve()
    
    # Get history
    history = ga.get_evolution_history()
    
    print(f"\nGenerations: {len(history['generations'])}")
    print(f"Final best fitness: {history['best_fitness'][-1]:.4f}")
# test_ga.py
from aes_custom import CustomAES, SecurityMetrics
from ga_optimizer import GeneticAlgorithm

# Create GA
ga = GeneticAlgorithm(
    custom_aes_class=CustomAES,
    security_metrics_class=SecurityMetrics,
    population_size=15,
    num_generations=10  # Quick test
)

# Run evolution
best = ga.evolve()

print(f"\nBest Configuration:")
print(f"Rotations: {best.rotations}")
print(f"Rcon Multipliers: {best.rcon_multipliers}")
print(f"Fitness: {best.fitness:.4f}")
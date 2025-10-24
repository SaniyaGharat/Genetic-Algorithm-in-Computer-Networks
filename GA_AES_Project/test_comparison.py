# test_comparison.py
from aes_custom import CustomAES, SecurityMetrics
from testing_visualization import ComprehensiveTester, Visualizer

# Standard vs Optimized
standard_params = {
    'rotations': [1]*10,
    'rcon_multipliers': [1]*10
}

# Use parameters from your GA run
optimized_params = {
    'rotations': [1, 2, 1, 3, 1, 2, 1, 1, 2, 1],
    'rcon_multipliers': [1, 1, 2, 1, 1, 3, 1, 1, 1, 2]
}

# Run comparison
tester = ComprehensiveTester(CustomAES, SecurityMetrics)
results = tester.compare_configurations(standard_params, optimized_params, num_tests=100)

# Visualize
viz = Visualizer()
viz.plot_comparison_metrics(results)
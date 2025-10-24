# test_network.py
from network_simulator import NetworkPerformanceTester

tester = NetworkPerformanceTester()

# Standard AES
standard_params = {'rotations': [1]*10, 'rcon_multipliers': [1]*10}
tester.run_test(standard_params, 'Standard AES', num_clients=3, messages_per_client=30)

# Optimized AES
optimized_params = {'rotations': [1,2,1,3,1,2,1,1,2,1], 'rcon_multipliers': [1,1,2,1,1,3,1,1,1,2]}
tester.run_test(optimized_params, 'GA-Optimized AES', num_clients=3, messages_per_client=30)

# Compare and plot
tester.compare_tests()
tester.plot_comparison()
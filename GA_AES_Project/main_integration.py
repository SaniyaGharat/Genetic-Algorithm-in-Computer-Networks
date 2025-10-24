"""
Main Integration Script for GA-Optimized AES Project
Runs the complete workflow: GA evolution → Testing → Visualization
"""

from aes_custom import CustomAES, SecurityMetrics
from ga_optimizer import GeneticAlgorithm, KeyScheduleChromosome
from testing_visualization import ComprehensiveTester, Visualizer
from Crypto.Random import get_random_bytes
import json
import os
from datetime import datetime


class ProjectPipeline:
    """
    Complete project pipeline orchestrator
    """
    
    def __init__(self, output_dir='results'):
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join(output_dir, f'run_{self.timestamp}')
        
        # Create output directory
        os.makedirs(self.run_dir, exist_ok=True)
        
        print(f"Output directory: {self.run_dir}\n")
    
    def run_complete_pipeline(self, ga_params=None):
        """
        Execute the complete project workflow
        """
        print("="*70)
        print("GA-OPTIMIZED AES KEY SCHEDULE PROJECT")
        print("="*70)
        print()
        
        # Default GA parameters
        if ga_params is None:
            ga_params = {
                'population_size': 25,
                'crossover_rate': 0.8,
                'mutation_rate': 0.2,
                'num_generations': 30,
                'elitism_count': 2
            }
        
        # PHASE 1: Run Genetic Algorithm
        print("PHASE 1: GENETIC ALGORITHM OPTIMIZATION")
        print("-"*70)
        
        ga = GeneticAlgorithm(
            custom_aes_class=CustomAES,
            security_metrics_class=SecurityMetrics,
            **ga_params
        )
        
        best_chromosome = ga.evolve()
        
        # Save GA results
        history = ga.get_evolution_history()
        with open(os.path.join(self.run_dir, 'ga_history.json'), 'w') as f:
            json.dump(history, f, indent=2)
        
        with open(os.path.join(self.run_dir, 'best_chromosome.json'), 'w') as f:
            json.dump({
                'rotations': best_chromosome.rotations,
                'rcon_multipliers': best_chromosome.rcon_multipliers,
                'fitness': best_chromosome.fitness,
                'metrics': best_chromosome.metrics
            }, f, indent=2)
        
        print(f"\nGA results saved to {self.run_dir}")
        print()
        
        # PHASE 2: Comprehensive Testing
        print("\nPHASE 2: COMPREHENSIVE TESTING")
        print("-"*70)
        
        standard_params = {
            'rotations': [1] * 10,
            'rcon_multipliers': [1] * 10
        }
        
        optimized_params = best_chromosome.to_params()
        
        tester = ComprehensiveTester(CustomAES, SecurityMetrics)
        results = tester.compare_configurations(
            standard_params, 
            optimized_params, 
            num_tests=100
        )
        
        tester.save_results(os.path.join(self.run_dir, 'comparison_results.json'))
        print()
        
        # PHASE 3: Visualization
        print("\nPHASE 3: GENERATING VISUALIZATIONS")
        print("-"*70)
        
        viz = Visualizer()
        
        # Plot 1: GA Evolution
        viz.plot_ga_evolution(
            history, 
            save_path=os.path.join(self.run_dir, 'ga_evolution.png')
        )
        
        # Plot 2: Comparison Metrics
        viz.plot_comparison_metrics(
            results,
            save_path=os.path.join(self.run_dir, 'comparison_metrics.png')
        )
        
        # Plot 3: Avalanche Distribution
        standard_aes = CustomAES(standard_params)
        optimized_aes = CustomAES(optimized_params)
        test_key = get_random_bytes(16)
        
        viz.plot_detailed_avalanche(
            standard_aes,
            optimized_aes,
            test_key,
            num_tests=50,
            save_path=os.path.join(self.run_dir, 'avalanche_distribution.png')
        )
        
        # Generate summary report
        viz.create_summary_report(
            results,
            best_chromosome,
            save_path=os.path.join(self.run_dir, 'summary_report.txt')
        )
        
        print()
        
        # PHASE 4: Final Summary
        print("\nPHASE 4: FINAL SUMMARY")
        print("-"*70)
        self.print_final_summary(best_chromosome, results)
        
        print("\n" + "="*70)
        print(f"All results saved to: {self.run_dir}")
        print("="*70)
        
        return {
            'best_chromosome': best_chromosome,
            'results': results,
            'history': history,
            'output_dir': self.run_dir
        }
    
    def print_final_summary(self, best_chromosome, results):
        """
        Print final summary to console
        """
        std = results['standard']
        opt = results['optimized']
        
        print(f"\nBest Configuration Found:")
        print(f"  Rotations: {best_chromosome.rotations}")
        print(f"  Rcon Multipliers: {best_chromosome.rcon_multipliers}")
        print(f"  Fitness: {best_chromosome.fitness:.4f}")
        
        print(f"\nKey Improvements:")
        
        # Avalanche improvement
        avalanche_diff = abs(50 - opt['avalanche_mean']) - abs(50 - std['avalanche_mean'])
        if avalanche_diff < 0:
            print(f"  ✓ Avalanche effect closer to ideal by {abs(avalanche_diff):.2f}%")
        
        # Speed improvement
        speed_improvement = ((std['encryption_time'] - opt['encryption_time']) / 
                            std['encryption_time'] * 100)
        if speed_improvement > 0:
            print(f"  ✓ Encryption speed improved by {speed_improvement:.2f}%")
        else:
            print(f"  ✗ Encryption speed decreased by {abs(speed_improvement):.2f}%")
        
        # Entropy improvement
        entropy_improvement = ((opt['entropy'] - std['entropy']) / std['entropy'] * 100)
        if entropy_improvement > 0:
            print(f"  ✓ Key schedule entropy improved by {entropy_improvement:.2f}%")
        else:
            print(f"  ✗ Key schedule entropy decreased by {abs(entropy_improvement):.2f}%")
        
        # Overall assessment
        improvements = sum([
            avalanche_diff < 0,
            speed_improvement > 0,
            entropy_improvement > 0
        ])
        
        print(f"\nOverall: {improvements}/3 metrics improved")


def quick_test():
    """
    Quick test with reduced parameters for fast execution
    """
    print("Running Quick Test (Reduced Parameters)...\n")
    
    pipeline = ProjectPipeline(output_dir='results_quick_test')
    
    quick_params = {
        'population_size': 15,
        'crossover_rate': 0.8,
        'mutation_rate': 0.2,
        'num_generations': 10,
        'elitism_count': 2
    }
    
    results = pipeline.run_complete_pipeline(ga_params=quick_params)
    
    return results


def full_run():
    """
    Full project run with recommended parameters
    """
    print("Running Full Project Pipeline...\n")
    
    pipeline = ProjectPipeline(output_dir='results')
    
    full_params = {
        'population_size': 25,
        'crossover_rate': 0.8,
        'mutation_rate': 0.2,
        'num_generations': 30,
        'elitism_count': 2
    }
    
    results = pipeline.run_complete_pipeline(ga_params=full_params)
    
    return results


# Main execution
if __name__ == "__main__":
    import sys
    
    print("GA-Optimized AES Key Schedule Project")
    print("Choose execution mode:")
    print("1. Quick Test (10 generations, ~5 minutes)")
    print("2. Full Run (30 generations, ~15 minutes)")
    print("3. Custom Parameters")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == '1':
        results = quick_test()
    elif choice == '2':
        results = full_run()
    elif choice == '3':
        print("\nEnter custom GA parameters:")
        pop_size = int(input("Population size (default 25): ") or 25)
        crossover = float(input("Crossover rate (default 0.8): ") or 0.8)
        mutation = float(input("Mutation rate (default 0.2): ") or 0.2)
        generations = int(input("Number of generations (default 30): ") or 30)
        elitism = int(input("Elitism count (default 2): ") or 2)
        
        pipeline = ProjectPipeline(output_dir='results')
        custom_params = {
            'population_size': pop_size,
            'crossover_rate': crossover,
            'mutation_rate': mutation,
            'num_generations': generations,
            'elitism_count': elitism
        }
        results = pipeline.run_complete_pipeline(ga_params=custom_params)
    else:
        print("Invalid choice. Running quick test...")
        results = quick_test()
    
    print("\n✓ Project execution complete!")
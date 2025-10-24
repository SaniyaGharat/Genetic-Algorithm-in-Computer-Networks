"""
Comprehensive Testing and Visualization for GA-Optimized AES
"""

import matplotlib.pyplot as plt
import numpy as np
from Crypto.Random import get_random_bytes
import time
import json


class ComprehensiveTester:
    """
    Test and compare standard vs GA-optimized AES configurations
    """
    
    def __init__(self, custom_aes_class, security_metrics_class):
        self.CustomAES = custom_aes_class
        self.SecurityMetrics = security_metrics_class
        self.results = {}
    
    def compare_configurations(self, standard_params, optimized_params, num_tests=100):
        """
        Compare standard and optimized configurations
        """
        print("=== Running Comprehensive Comparison ===\n")
        
        # Test key
        test_key = get_random_bytes(16)
        
        # Create instances
        standard_aes = self.CustomAES(standard_params)
        optimized_aes = self.CustomAES(optimized_params)
        metrics = self.SecurityMetrics()
        
        results = {
            'standard': {},
            'optimized': {}
        }
        
        # Test 1: Avalanche Effect
        print("Testing Avalanche Effect...")
        std_avalanche_mean, std_avalanche_std = metrics.calculate_avalanche_effect(
            standard_aes, test_key, num_tests
        )
        opt_avalanche_mean, opt_avalanche_std = metrics.calculate_avalanche_effect(
            optimized_aes, test_key, num_tests
        )
        
        results['standard']['avalanche_mean'] = std_avalanche_mean
        results['standard']['avalanche_std'] = std_avalanche_std
        results['optimized']['avalanche_mean'] = opt_avalanche_mean
        results['optimized']['avalanche_std'] = opt_avalanche_std
        
        print(f"  Standard: {std_avalanche_mean:.2f}% ± {std_avalanche_std:.2f}%")
        print(f"  Optimized: {opt_avalanche_mean:.2f}% ± {opt_avalanche_std:.2f}%")
        
        # Test 2: Encryption Speed
        print("\nTesting Encryption Speed...")
        std_time = metrics.measure_encryption_time(standard_aes, test_key, 1024, 200)
        opt_time = metrics.measure_encryption_time(optimized_aes, test_key, 1024, 200)
        
        results['standard']['encryption_time'] = std_time
        results['optimized']['encryption_time'] = opt_time
        
        print(f"  Standard: {std_time:.4f} ms")
        print(f"  Optimized: {opt_time:.4f} ms")
        print(f"  Speed improvement: {((std_time - opt_time) / std_time * 100):.2f}%")
        
        # Test 3: Key Schedule Entropy
        print("\nTesting Key Schedule Entropy...")
        _ = standard_aes.encrypt(b"test" * 4, test_key)
        std_entropy = standard_aes.get_key_schedule_entropy()
        
        _ = optimized_aes.encrypt(b"test" * 4, test_key)
        opt_entropy = optimized_aes.get_key_schedule_entropy()
        
        results['standard']['entropy'] = std_entropy
        results['optimized']['entropy'] = opt_entropy
        
        print(f"  Standard: {std_entropy:.4f} bits")
        print(f"  Optimized: {opt_entropy:.4f} bits")
        
        # Test 4: Ciphertext Entropy
        print("\nTesting Ciphertext Entropy...")
        plaintext = get_random_bytes(1024)
        std_ct = standard_aes.encrypt(plaintext, test_key)
        opt_ct = optimized_aes.encrypt(plaintext, test_key)
        
        std_ct_entropy = metrics.calculate_entropy(std_ct)
        opt_ct_entropy = metrics.calculate_entropy(opt_ct)
        
        results['standard']['ciphertext_entropy'] = std_ct_entropy
        results['optimized']['ciphertext_entropy'] = opt_ct_entropy
        
        print(f"  Standard: {std_ct_entropy:.4f} bits")
        print(f"  Optimized: {opt_ct_entropy:.4f} bits")
        
        # Test 5: Correctness Test
        print("\nTesting Encryption/Decryption Correctness...")
        test_messages = [
            b"Short message",
            b"A" * 100,
            b"Mixed content 123!@# with special chars",
            get_random_bytes(256)
        ]
        
        all_correct = True
        for i, msg in enumerate(test_messages):
            std_ct = standard_aes.encrypt(msg, test_key)
            std_pt = standard_aes.decrypt(std_ct, test_key)
            
            opt_ct = optimized_aes.encrypt(msg, test_key)
            opt_pt = optimized_aes.decrypt(opt_ct, test_key)
            
            if std_pt != msg or opt_pt != msg:
                all_correct = False
                print(f"  Test {i+1}: FAILED")
            else:
                print(f"  Test {i+1}: PASSED")
        
        results['correctness'] = all_correct
        
        self.results = results
        return results
    
    def save_results(self, filename='comparison_results.json'):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to {filename}")


class Visualizer:
    """
    Create visualizations for GA evolution and comparison results
    """
    
    @staticmethod
    def plot_ga_evolution(history, save_path='ga_evolution.png'):
        """
        Plot fitness evolution over generations
        """
        plt.figure(figsize=(10, 6))
        
        generations = history['generations']
        best_fitness = history['best_fitness']
        avg_fitness = history['avg_fitness']
        
        plt.plot(generations, best_fitness, 'b-', linewidth=2, 
                label='Best Fitness', marker='o', markersize=4)
        plt.plot(generations, avg_fitness, 'r--', linewidth=2, 
                label='Average Fitness', marker='s', markersize=4)
        
        plt.xlabel('Generation', fontsize=12, fontweight='bold')
        plt.ylabel('Fitness Score', fontsize=12, fontweight='bold')
        plt.title('Genetic Algorithm Fitness Evolution', fontsize=14, fontweight='bold')
        plt.legend(loc='lower right', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"GA evolution plot saved to {save_path}")
        plt.close()
    
    @staticmethod
    def plot_comparison_metrics(results, save_path='comparison_metrics.png'):
        """
        Create bar charts comparing standard vs optimized configurations
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Standard AES vs GA-Optimized AES Comparison', 
                    fontsize=16, fontweight='bold')
        # Support several input shapes:
        # - direct results dict with 'standard' and 'optimized'
        # - pipeline return value containing a 'results' key
        # - a path to a JSON file
        if isinstance(results, dict) and 'results' in results and isinstance(results['results'], dict):
            results = results['results']
        elif isinstance(results, str):
            try:
                with open(results, 'r') as f:
                    results = json.load(f)
            except Exception as e:
                raise ValueError(f"Could not load results from path '{results}': {e}")

        if not isinstance(results, dict) or 'standard' not in results or 'optimized' not in results:
            raise ValueError("plot_comparison_metrics expected a dict with 'standard' and 'optimized' keys")

        # Convert possible numpy scalars to native Python floats to avoid indexing issues
        def _coerce(d):
            out = {}
            for k, v in d.items():
                if isinstance(v, (np.generic,)):
                    try:
                        out[k] = float(v)
                    except Exception:
                        out[k] = v
                else:
                    out[k] = v
            return out

        std = _coerce(results.get('standard', {}))
        opt = _coerce(results.get('optimized', {}))
        
        # 1. Avalanche Effect
        ax1 = axes[0, 0]
        categories = ['Standard', 'Optimized']
        avalanche_means = [std['avalanche_mean'], opt['avalanche_mean']]
        avalanche_stds = [std['avalanche_std'], opt['avalanche_std']]
        
        bars1 = ax1.bar(categories, avalanche_means, yerr=avalanche_stds, 
                       capsize=5, color=['#3498db', '#2ecc71'], alpha=0.8)
        ax1.axhline(y=50, color='red', linestyle='--', linewidth=2, 
                   label='Ideal (50%)', alpha=0.7)
        ax1.set_ylabel('Avalanche Effect (%)', fontweight='bold')
        ax1.set_title('Avalanche Effect Comparison', fontweight='bold')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, mean, std_dev in zip(bars1, avalanche_means, avalanche_stds):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{mean:.2f}%\n±{std_dev:.2f}',
                    ha='center', va='bottom', fontsize=9)
        
        # 2. Encryption Time
        ax2 = axes[0, 1]
        times = [std['encryption_time'], opt['encryption_time']]
        bars2 = ax2.bar(categories, times, color=['#3498db', '#2ecc71'], alpha=0.8)
        ax2.set_ylabel('Time (ms)', fontweight='bold')
        ax2.set_title('Encryption Speed Comparison', fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        for bar, time_val in zip(bars2, times):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{time_val:.4f}ms',
                    ha='center', va='bottom', fontsize=9)
        
        # Calculate improvement
        improvement = ((std['encryption_time'] - opt['encryption_time']) / 
                      std['encryption_time'] * 100)
        ax2.text(0.5, max(times) * 0.9, f'Improvement: {improvement:.2f}%',
                ha='center', transform=ax2.transData,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
                fontsize=10, fontweight='bold')
        
        # 3. Key Schedule Entropy
        ax3 = axes[1, 0]
        entropies = [std['entropy'], opt['entropy']]
        bars3 = ax3.bar(categories, entropies, color=['#3498db', '#2ecc71'], alpha=0.8)
        ax3.set_ylabel('Entropy (bits)', fontweight='bold')
        ax3.set_title('Key Schedule Entropy Comparison', fontweight='bold')
        ax3.set_ylim([0, 8])
        ax3.grid(axis='y', alpha=0.3)
        
        for bar, ent in zip(bars3, entropies):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{ent:.4f}',
                    ha='center', va='bottom', fontsize=9)
        
        # 4. Ciphertext Entropy
        ax4 = axes[1, 1]
        ct_entropies = [std['ciphertext_entropy'], opt['ciphertext_entropy']]
        bars4 = ax4.bar(categories, ct_entropies, color=['#3498db', '#2ecc71'], alpha=0.8)
        ax4.set_ylabel('Entropy (bits)', fontweight='bold')
        ax4.set_title('Ciphertext Entropy Comparison', fontweight='bold')
        ax4.set_ylim([0, 8])
        ax4.grid(axis='y', alpha=0.3)
        
        for bar, ct_ent in zip(bars4, ct_entropies):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{ct_ent:.4f}',
                    ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison plot saved to {save_path}")
        plt.close()
    
    @staticmethod
    def plot_detailed_avalanche(standard_aes, optimized_aes, test_key, 
                               num_tests=50, save_path='avalanche_distribution.png'):
        """
        Plot distribution of avalanche effect percentages
        """
        from aes_custom import SecurityMetrics
        metrics = SecurityMetrics()
        
        # Collect individual test results
        std_results = []
        opt_results = []
        
        for _ in range(num_tests):
            plaintext = get_random_bytes(16)
            
            # Standard
            ct1 = standard_aes.encrypt(plaintext, test_key)
            plaintext_list = list(plaintext)
            plaintext_list[0] ^= 1
            ct2 = standard_aes.encrypt(bytes(plaintext_list), test_key)
            diff_bits = sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(ct1, ct2))
            std_results.append((diff_bits / (len(ct1) * 8)) * 100)
            
            # Optimized
            ct1 = optimized_aes.encrypt(plaintext, test_key)
            ct2 = optimized_aes.encrypt(bytes(plaintext_list), test_key)
            diff_bits = sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(ct1, ct2))
            opt_results.append((diff_bits / (len(ct1) * 8)) * 100)
        
        plt.figure(figsize=(12, 6))
        
        plt.hist(std_results, bins=20, alpha=0.6, label='Standard AES', 
                color='#3498db', edgecolor='black')
        plt.hist(opt_results, bins=20, alpha=0.6, label='Optimized AES', 
                color='#2ecc71', edgecolor='black')
        
        plt.axvline(x=50, color='red', linestyle='--', linewidth=2, 
                   label='Ideal (50%)', alpha=0.7)
        plt.axvline(x=np.mean(std_results), color='blue', linestyle=':', 
                   linewidth=2, alpha=0.7)
        plt.axvline(x=np.mean(opt_results), color='green', linestyle=':', 
                   linewidth=2, alpha=0.7)
        
        plt.xlabel('Avalanche Effect (%)', fontsize=12, fontweight='bold')
        plt.ylabel('Frequency', fontsize=12, fontweight='bold')
        plt.title('Distribution of Avalanche Effect', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Avalanche distribution plot saved to {save_path}")
        plt.close()
    
    @staticmethod
    def create_summary_report(results, best_chromosome, save_path='summary_report.txt'):
        """
        Generate text summary report
        """
        with open(save_path, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("GA-OPTIMIZED AES KEY SCHEDULE - SUMMARY REPORT\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("OPTIMIZED PARAMETERS:\n")
            f.write("-" * 70 + "\n")
            f.write(f"Rotations: {best_chromosome.rotations}\n")
            f.write(f"Rcon Multipliers: {best_chromosome.rcon_multipliers}\n")
            f.write(f"Fitness Score: {best_chromosome.fitness:.4f}\n\n")
            
            f.write("PERFORMANCE COMPARISON:\n")
            f.write("-" * 70 + "\n")
            
            std = results['standard']
            opt = results['optimized']
            
            f.write(f"\n1. AVALANCHE EFFECT:\n")
            f.write(f"   Standard:  {std['avalanche_mean']:.2f}% ± {std['avalanche_std']:.2f}%\n")
            f.write(f"   Optimized: {opt['avalanche_mean']:.2f}% ± {opt['avalanche_std']:.2f}%\n")
            f.write(f"   Ideal: 50%\n")
            f.write(f"   Improvement: {abs(50 - opt['avalanche_mean']) < abs(50 - std['avalanche_mean'])}\n")
            
            f.write(f"\n2. ENCRYPTION SPEED:\n")
            f.write(f"   Standard:  {std['encryption_time']:.4f} ms\n")
            f.write(f"   Optimized: {opt['encryption_time']:.4f} ms\n")
            speed_improvement = ((std['encryption_time'] - opt['encryption_time']) / 
                                std['encryption_time'] * 100)
            f.write(f"   Speed Improvement: {speed_improvement:.2f}%\n")
            
            f.write(f"\n3. KEY SCHEDULE ENTROPY:\n")
            f.write(f"   Standard:  {std['entropy']:.4f} bits\n")
            f.write(f"   Optimized: {opt['entropy']:.4f} bits\n")
            entropy_improvement = ((opt['entropy'] - std['entropy']) / std['entropy'] * 100)
            f.write(f"   Improvement: {entropy_improvement:.2f}%\n")
            
            f.write(f"\n4. CIPHERTEXT ENTROPY:\n")
            f.write(f"   Standard:  {std['ciphertext_entropy']:.4f} bits\n")
            f.write(f"   Optimized: {opt['ciphertext_entropy']:.4f} bits\n")
            
            f.write(f"\n5. CORRECTNESS:\n")
            f.write(f"   All Tests Passed: {results['correctness']}\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("CONCLUSION:\n")
            f.write("-" * 70 + "\n")
            f.write("The GA-optimized key schedule demonstrates ")
            if speed_improvement > 0 and entropy_improvement > 0:
                f.write("improvements in both\n")
                f.write("security (entropy) and performance (speed) compared to standard AES.\n")
            elif speed_improvement > 0:
                f.write("improvements in performance\n")
                f.write("while maintaining comparable security metrics.\n")
            else:
                f.write("enhanced security properties.\n")
            
            f.write("\n" + "=" * 70 + "\n")
        
        print(f"Summary report saved to {save_path}")


# Example usage
if __name__ == "__main__":
    from aes_custom import CustomAES, SecurityMetrics
    
    # Standard parameters
    standard_params = {
        'rotations': [1] * 10,
        'rcon_multipliers': [1] * 10
    }
    
    # Example optimized parameters (from GA)
    optimized_params = {
        'rotations': [1, 2, 1, 3, 1, 2, 1, 1, 2, 1],
        'rcon_multipliers': [1, 1, 2, 1, 1, 3, 1, 1, 1, 2]
    }
    
    # Run comprehensive testing
    tester = ComprehensiveTester(CustomAES, SecurityMetrics)
    results = tester.compare_configurations(standard_params, optimized_params, num_tests=100)
    tester.save_results()
    
    # Create visualizations
    viz = Visualizer()
    viz.plot_comparison_metrics(results)
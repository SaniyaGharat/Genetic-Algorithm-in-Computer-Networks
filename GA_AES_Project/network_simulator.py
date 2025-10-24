"""
Network Performance Simulator - Simulates encrypted client-server communication
Measures end-to-end latency including encryption overhead
"""

import socket
import threading
import time
import random
from queue import Queue
import numpy as np
import matplotlib.pyplot as plt
from aes_custom import CustomAES, SecurityMetrics
from Crypto.Random import get_random_bytes


class NetworkSimulator:
    """
    Simulates network with encryption overhead
    """
    
    def __init__(self, base_latency_ms=2.0, jitter_ms=0.5):
        """
        Args:
            base_latency_ms: Base network latency in milliseconds
            jitter_ms: Random jitter variation
        """
        self.base_latency = base_latency_ms / 1000  # Convert to seconds
        self.jitter = jitter_ms / 1000
    
    def simulate_network_delay(self):
        """Simulate network latency with jitter"""
        delay = self.base_latency + random.uniform(-self.jitter, self.jitter)
        time.sleep(max(0, delay))
        return delay * 1000  # Return in ms


class SecureServer:
    """
    Simulated secure server with encryption
    """
    
    def __init__(self, aes_params=None, network_sim=None):
        self.aes = CustomAES(aes_params)
        self.key = get_random_bytes(16)
        self.network_sim = network_sim or NetworkSimulator()
        self.metrics = []
        self.lock = threading.Lock()
        
    def handle_request(self, client_id, encrypted_data):
        """
        Handle encrypted request from client
        Returns: dict with timing metrics
        """
        start_time = time.time()
        
        # Simulate network receive delay
        network_delay = self.network_sim.simulate_network_delay()
        
        # Decrypt data
        decrypt_start = time.time()
        try:
            decrypted_data = self.aes.decrypt(encrypted_data, self.key)
            decrypt_time = (time.time() - decrypt_start) * 1000
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
        
        # Process (simulate)
        processing_time = random.uniform(0.1, 0.5)
        time.sleep(processing_time / 1000)
        
        # Encrypt response
        encrypt_start = time.time()
        response = self.aes.encrypt(b"ACK: " + decrypted_data[:20], self.key)
        encrypt_time = (time.time() - encrypt_start) * 1000
        
        # Simulate network send delay
        network_delay += self.network_sim.simulate_network_delay()
        
        total_time = (time.time() - start_time) * 1000
        
        metrics = {
            'client_id': client_id,
            'network_delay': network_delay,
            'decrypt_time': decrypt_time,
            'encrypt_time': encrypt_time,
            'processing_time': processing_time,
            'total_time': total_time
        }
        
        with self.lock:
            self.metrics.append(metrics)
        
        return metrics
    
    def get_metrics(self):
        """Return collected metrics"""
        with self.lock:
            return self.metrics.copy()


class SecureClient:
    """
    Simulated secure client
    """
    
    def __init__(self, client_id, server, aes_params=None):
        self.client_id = client_id
        self.server = server
        self.aes = CustomAES(aes_params)
        self.key = server.key  # Shared key
        self.results = []
    
    def send_message(self, message):
        """
        Send encrypted message to server
        """
        start_time = time.time()
        
        # Encrypt message
        encrypt_start = time.time()
        encrypted_data = self.aes.encrypt(message.encode(), self.key)
        encrypt_time = (time.time() - encrypt_start) * 1000
        
        # Send to server
        server_metrics = self.server.handle_request(self.client_id, encrypted_data)
        
        if server_metrics:
            total_time = (time.time() - start_time) * 1000
            
            result = {
                'client_id': self.client_id,
                'client_encrypt_time': encrypt_time,
                'server_metrics': server_metrics,
                'end_to_end_time': total_time
            }
            
            self.results.append(result)
            return result
        
        return None
    
    def get_results(self):
        """Return all results"""
        return self.results.copy()


class NetworkPerformanceTester:
    """
    Comprehensive network performance testing with encryption
    """
    
    def __init__(self):
        self.results = {}
    
    def run_test(self, aes_params, test_name, num_clients=3, 
                 messages_per_client=50, network_latency=2.0):
        """
        Run complete test with multiple clients
        
        Args:
            aes_params: AES configuration parameters
            test_name: Name for this test (e.g., 'Standard' or 'Optimized')
            num_clients: Number of concurrent clients
            messages_per_client: Messages each client sends
            network_latency: Base network latency in ms
        """
        print(f"\n{'='*60}")
        print(f"Running Test: {test_name}")
        print(f"{'='*60}")
        print(f"Clients: {num_clients}, Messages per client: {messages_per_client}")
        print(f"Network latency: {network_latency}ms\n")
        
        # Create network simulator
        network_sim = NetworkSimulator(base_latency_ms=network_latency, jitter_ms=0.3)
        
        # Create server
        server = SecureServer(aes_params=aes_params, network_sim=network_sim)
        
        # Create clients
        clients = [SecureClient(i+1, server, aes_params) 
                  for i in range(num_clients)]
        
        # Run tests
        start_time = time.time()
        
        threads = []
        for client in clients:
            thread = threading.Thread(
                target=self._client_worker,
                args=(client, messages_per_client)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        total_duration = time.time() - start_time
        
        # Collect results
        all_client_results = []
        for client in clients:
            all_client_results.extend(client.get_results())
        
        server_metrics = server.get_metrics()
        
        # Calculate statistics
        stats = self._calculate_statistics(all_client_results, server_metrics)
        stats['test_name'] = test_name
        stats['total_duration'] = total_duration
        stats['total_messages'] = num_clients * messages_per_client
        stats['throughput'] = (num_clients * messages_per_client) / total_duration
        
        self.results[test_name] = {
            'stats': stats,
            'client_results': all_client_results,
            'server_metrics': server_metrics
        }
        
        # Print summary
        self._print_test_summary(stats)
        
        return stats
    
    def _client_worker(self, client, num_messages):
        """Worker function for client thread"""
        messages = [
            f"Message {i+1} from Client {client.client_id}"
            for i in range(num_messages)
        ]
        
        for msg in messages:
            client.send_message(msg)
            time.sleep(random.uniform(0.01, 0.05))  # Small delay between messages
    
    def _calculate_statistics(self, client_results, server_metrics):
        """Calculate performance statistics"""
        
        # Client-side encryption times
        client_encrypt_times = [r['client_encrypt_time'] for r in client_results]
        
        # Server-side metrics
        server_decrypt_times = [m['decrypt_time'] for m in server_metrics]
        server_encrypt_times = [m['encrypt_time'] for m in server_metrics]
        network_delays = [m['network_delay'] for m in server_metrics]
        total_times = [m['total_time'] for m in server_metrics]
        
        # End-to-end times
        e2e_times = [r['end_to_end_time'] for r in client_results]
        
        stats = {
            'client_encrypt': {
                'mean': np.mean(client_encrypt_times),
                'std': np.std(client_encrypt_times),
                'min': np.min(client_encrypt_times),
                'max': np.max(client_encrypt_times)
            },
            'server_decrypt': {
                'mean': np.mean(server_decrypt_times),
                'std': np.std(server_decrypt_times),
                'min': np.min(server_decrypt_times),
                'max': np.max(server_decrypt_times)
            },
            'server_encrypt': {
                'mean': np.mean(server_encrypt_times),
                'std': np.std(server_encrypt_times),
                'min': np.min(server_encrypt_times),
                'max': np.max(server_encrypt_times)
            },
            'network_delay': {
                'mean': np.mean(network_delays),
                'std': np.std(network_delays),
                'min': np.min(network_delays),
                'max': np.max(network_delays)
            },
            'end_to_end': {
                'mean': np.mean(e2e_times),
                'std': np.std(e2e_times),
                'min': np.min(e2e_times),
                'max': np.max(e2e_times)
            },
            'total_encryption_overhead': {
                'mean': np.mean(client_encrypt_times) + 
                        np.mean(server_decrypt_times) + 
                        np.mean(server_encrypt_times)
            }
        }
        
        return stats
    
    def _print_test_summary(self, stats):
        """Print test summary"""
        print(f"\nTest Results Summary:")
        print(f"-" * 60)
        print(f"Client Encryption:   {stats['client_encrypt']['mean']:.4f}ms ± {stats['client_encrypt']['std']:.4f}ms")
        print(f"Server Decryption:   {stats['server_decrypt']['mean']:.4f}ms ± {stats['server_decrypt']['std']:.4f}ms")
        print(f"Server Encryption:   {stats['server_encrypt']['mean']:.4f}ms ± {stats['server_encrypt']['std']:.4f}ms")
        print(f"Network Delay:       {stats['network_delay']['mean']:.4f}ms ± {stats['network_delay']['std']:.4f}ms")
        print(f"End-to-End Latency:  {stats['end_to_end']['mean']:.4f}ms ± {stats['end_to_end']['std']:.4f}ms")
        print(f"Total Enc Overhead:  {stats['total_encryption_overhead']['mean']:.4f}ms")
        print(f"Messages Processed:  {stats['total_messages']}")
        print(f"Throughput:          {stats['throughput']:.2f} msg/s")
        print(f"Total Duration:      {stats['total_duration']:.2f}s")
    
    def compare_tests(self):
        """Compare all test results"""
        if len(self.results) < 2:
            print("Need at least 2 tests to compare")
            return
        
        print(f"\n{'='*60}")
        print("COMPARATIVE ANALYSIS")
        print(f"{'='*60}\n")
        
        test_names = list(self.results.keys())
        
        for metric in ['client_encrypt', 'server_decrypt', 'server_encrypt', 
                      'network_delay', 'end_to_end', 'total_encryption_overhead']:
            
            print(f"\n{metric.upper().replace('_', ' ')}:")
            print(f"-" * 60)
            
            for name in test_names:
                if metric == 'total_encryption_overhead':
                    value = self.results[name]['stats'][metric]['mean']
                    print(f"  {name:15s}: {value:.4f}ms")
                else:
                    stats = self.results[name]['stats'][metric]
                    print(f"  {name:15s}: {stats['mean']:.4f}ms ± {stats['std']:.4f}ms")
            
            # Calculate improvement
            if len(test_names) == 2:
                if metric == 'total_encryption_overhead':
                    val1 = self.results[test_names[0]]['stats'][metric]['mean']
                    val2 = self.results[test_names[1]]['stats'][metric]['mean']
                else:
                    val1 = self.results[test_names[0]]['stats'][metric]['mean']
                    val2 = self.results[test_names[1]]['stats'][metric]['mean']
                
                improvement = ((val1 - val2) / val1) * 100
                print(f"  {'Improvement:':15s} {improvement:+.2f}%")
    
    def plot_comparison(self, save_path='network_comparison.png'):
        """Create comparison visualization"""
        if len(self.results) < 2:
            print("Need at least 2 tests to plot comparison")
            return
        
        test_names = list(self.results.keys())
        metrics = ['client_encrypt', 'server_decrypt', 'server_encrypt', 
                  'network_delay', 'end_to_end']
        metric_labels = ['Client Encrypt', 'Server Decrypt', 'Server Encrypt',
                        'Network Delay', 'End-to-End']
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Network Performance Comparison with Encryption', 
                    fontsize=16, fontweight='bold')
        
        axes = axes.flatten()
        
        for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
            ax = axes[idx]
            
            means = [self.results[name]['stats'][metric]['mean'] 
                    for name in test_names]
            stds = [self.results[name]['stats'][metric]['std'] 
                   for name in test_names]
            
            bars = ax.bar(test_names, means, yerr=stds, capsize=5,
                         color=['#3498db', '#2ecc71'], alpha=0.8)
            
            ax.set_ylabel('Time (ms)', fontweight='bold')
            ax.set_title(label, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for bar, mean in zip(bars, means):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{mean:.3f}ms',
                       ha='center', va='bottom', fontsize=9)
        
        # Throughput comparison
        ax = axes[5]
        throughputs = [self.results[name]['stats']['throughput'] 
                      for name in test_names]
        bars = ax.bar(test_names, throughputs, color=['#3498db', '#2ecc71'], alpha=0.8)
        ax.set_ylabel('Messages/second', fontweight='bold')
        ax.set_title('Throughput', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        for bar, tput in zip(bars, throughputs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{tput:.2f}',
                   ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nComparison plot saved to {save_path}")
        plt.close()


# Example usage
if __name__ == "__main__":
    # Create tester
    tester = NetworkPerformanceTester()
    
    # Test 1: Standard AES
    standard_params = {
        'rotations': [1] * 10,
        'rcon_multipliers': [1] * 10
    }
    
    tester.run_test(
        aes_params=standard_params,
        test_name='Standard AES',
        num_clients=3,
        messages_per_client=30,
        network_latency=2.0
    )
    
    # Test 2: GA-Optimized AES
    optimized_params = {
        'rotations': [1, 2, 1, 3, 1, 2, 1, 1, 2, 1],
        'rcon_multipliers': [1, 1, 2, 1, 1, 3, 1, 1, 1, 2]
    }
    
    tester.run_test(
        aes_params=optimized_params,
        test_name='GA-Optimized AES',
        num_clients=3,
        messages_per_client=30,
        network_latency=2.0
    )
    
    # Compare and visualize
    tester.compare_tests()
    tester.plot_comparison()
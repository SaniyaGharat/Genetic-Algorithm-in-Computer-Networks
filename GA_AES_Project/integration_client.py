"""
Integration Client
Connects to Packet Tracer network simulation
Sends GA-AES encrypted messages to server
"""

import socket
import time
import sys
from aes_custom import CustomAES
from network_bridge import network_bridge
from Crypto.Random import get_random_bytes

class IntegrationClient:
    def __init__(self, server_host='127.0.0.1', server_port=5000,
                 client_name="Client1", use_ga_optimization=True):
        """
        Integration Client with Packet Tracer bridge
        
        Args:
            server_host: Server IP address
            server_port: Server port
            client_name: Name of this client
            use_ga_optimization: Use GA-optimized or standard AES
        """
        self.server_host = server_host
        self.server_port = server_port
        self.client_name = client_name
        self.use_ga_optimization = use_ga_optimization
        
        # Initialize AES (same params as server)
        if use_ga_optimization:
            self.aes_params = {
                'rotations': [1, 2, 1, 3, 1, 2, 1, 1, 2, 1],
                'rcon_multipliers': [1, 1, 2, 1, 1, 3, 1, 1, 1, 2]
            }
            self.client_type = "GA-OPTIMIZED"
        else:
            self.aes_params = None
            self.client_type = "STANDARD"
        
        self.aes = CustomAES(self.aes_params)
        # Use a fixed key that matches the server
        self.key = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        
        self.latencies = []
        self.messages_sent = 0
    
    def send_message(self, message: str, retry_count=3) -> float:
        """
        Send encrypted message to server through Packet Tracer network
        
        Returns:
            Latency in milliseconds
        """
        for attempt in range(retry_count):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try:
                start_time = time.perf_counter()
                
                # Connect to server
                client_socket.connect((self.server_host, self.server_port))
                
                # Encrypt message
                encrypted = self.aes.encrypt(message.encode(), self.key)
                
                # Record packet in network bridge (simulating Packet Tracer)
                sent_packet = network_bridge.send_packet(
                    source_ip="127.0.0.1",
                    dest_ip=self.server_host,
                    payload=encrypted,
                    encryption_type="GA-AES" if self.use_ga_optimization else "Standard-AES"
                )
                
                # Send to server
                client_socket.send(encrypted)
                
                # Receive ACK
                response = client_socket.recv(4096)
                
                end_time = time.perf_counter()
                latency = (end_time - start_time) * 1000  # ms
                
                self.latencies.append(latency)
                self.messages_sent += 1
                
                encryption_time = self.aes.encryption_times[-1] if self.aes.encryption_times else 0
                
                print(f"\n✅ {self.client_name} sent message")
                print(f"   📨 Encrypted size: {len(encrypted)} bytes")
                print(f"   🔒 Encryption time: {encryption_time:.4f} ms")
                print(f"   ⏱️  Total latency: {latency:.2f} ms")
                print(f"   🌐 Network simulation: {sent_packet.latency_ms:.2f} ms")
                
                return latency
                
            except ConnectionRefusedError:
                if attempt < retry_count - 1:
                    print(f"⚠️  {self.client_name} - Connection refused. Retrying...")
                    time.sleep(1)
                else:
                    print(f"❌ {self.client_name} - Could not connect to server")
                    return None
            except Exception as e:
                print(f"❌ {self.client_name} - Error: {e}")
                return None
            finally:
                client_socket.close()
    
    def send_batch(self, num_messages=10, delay=0.5):
        """Send multiple messages"""
        print(f"\n{'='*70}")
        print(f"🚀 {self.client_name} - BATCH TEST [{self.client_type} AES]")
        print(f"{'='*70}")
        
        for i in range(num_messages):
            message = f"{self.client_name} - Test Message {i+1} for encryption testing"
            self.send_message(message)
            if i < num_messages - 1:
                time.sleep(delay)
        
        # Print client statistics
        self.print_statistics()
    
    def print_statistics(self):
        """Print client statistics"""
        if self.latencies:
            avg_latency = sum(self.latencies) / len(self.latencies)
            min_latency = min(self.latencies)
            max_latency = max(self.latencies)
            
            print(f"\n{'='*70}")
            print(f"📊 {self.client_name} STATISTICS - [{self.client_type} AES]")
            print(f"{'='*70}")
            print(f"  Messages sent:        {self.messages_sent}")
            print(f"  Average latency:      {avg_latency:.2f} ms")
            print(f"  Min latency:          {min_latency:.2f} ms")
            print(f"  Max latency:          {max_latency:.2f} ms")
            print(f"  Avg encryption time:  {self.aes.get_avg_encryption_time():.4f} ms")
            print(f"{'='*70}\n")

if __name__ == "__main__":
    # Check if --optimized flag is provided
    use_ga = "--optimized" in sys.argv
    client_name = "Client1"
    
    client = IntegrationClient(
        server_host='127.0.0.1',
        server_port=5000,
        client_name=client_name,
        use_ga_optimization=use_ga
    )
    
    # Send batch of messages
    client.send_batch(num_messages=5, delay=1)
"""
Integration Server
Connects to Packet Tracer network simulation
Uses GA-optimized AES encryption
"""

import socket
import json
import time
from aes_custom import CustomAES  # Your existing AES module
from network_bridge import network_bridge, NetworkPacket
from Crypto.Random import get_random_bytes

class IntegrationServer:
    def __init__(self, host='127.0.0.1', port=5000, 
                 use_ga_optimization=True):
        """
        Integration Server with Packet Tracer bridge
        
        Args:
            host: Server IP
            port: Server port
            use_ga_optimization: Use GA-optimized or standard AES
        """
        self.host = host
        self.port = port
        self.use_ga_optimization = use_ga_optimization
        
        # Initialize AES
        if use_ga_optimization:
            self.aes_params = {
                'rotations': [1, 2, 1, 3, 1, 2, 1, 1, 2, 1],
                'rcon_multipliers': [1, 1, 2, 1, 1, 3, 1, 1, 1, 2]
            }
            self.server_type = "GA-OPTIMIZED"
        else:
            self.aes_params = None
            self.server_type = "STANDARD"
        
        self.aes = CustomAES(self.aes_params)
        # Use the same fixed key as the client
        self.key = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        
        self.connection_count = 0
        self.total_bytes_received = 0
    
    def start(self):
        """Start the server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            print(f"\n{'='*70}")
            print(f"🔐 INTEGRATION SERVER - [{self.server_type} AES]")
            print(f"{'='*70}")
            print(f"📡 Server listening on {self.host}:{self.port}")
            print(f"🌐 Connected to Packet Tracer Bridge: YES")
            print(f"🧬 GA Optimization: {self.use_ga_optimization}")
            print(f"{'='*70}\n")
            
            while True:
                try:
                    client_socket, address = server_socket.accept()
                    self.connection_count += 1
                    client_ip = address[0]
                    
                    print(f"\n✅ Connection #{self.connection_count}")
                    print(f"   Client IP: {client_ip}:{address[1]}")
                    
                    # Receive encrypted data
                    encrypted_data = client_socket.recv(4096)
                    
                    if encrypted_data:
                        # Record packet in network bridge
                        sent_packet = network_bridge.send_packet(
                            source_ip=client_ip,
                            dest_ip=self.host,
                            payload=encrypted_data,
                            encryption_type="GA-AES" if self.use_ga_optimization else "Standard-AES"
                        )
                        
                        network_bridge.print_packet_trace(sent_packet)
                        
                        # Decrypt message
                        try:
                            decrypted = self.aes.decrypt(encrypted_data, self.key)
                            message_text = decrypted.decode()
                            
                            print(f"   🔓 Decrypted: {message_text}")
                            print(f"   ⏱️  Decryption time: {self.aes.decryption_times[-1]:.4f} ms")
                            
                            self.total_bytes_received += len(encrypted_data)
                            
                            # Send acknowledgment
                            ack_msg = f"✓ Received: {message_text}"
                            encrypted_ack = self.aes.encrypt(ack_msg.encode(), self.key)
                            
                            # Record ACK packet
                            ack_packet = network_bridge.send_packet(
                                source_ip=self.host,
                                dest_ip=client_ip,
                                payload=encrypted_ack,
                                encryption_type="GA-AES" if self.use_ga_optimization else "Standard-AES"
                            )
                            
                            client_socket.send(encrypted_ack)
                            print(f"   ✉️  ACK sent back to client\n")
                            
                        except Exception as e:
                            print(f"   ❌ Decryption error: {e}\n")
                    
                    client_socket.close()
                    
                except KeyboardInterrupt:
                    print(f"\n⛔ Server stopped by user\n")
                    break
                except Exception as e:
                    print(f"⚠️  Error: {e}\n")
                    continue
        
        except Exception as e:
            print(f"❌ Server error: {e}\n")
        
        finally:
            server_socket.close()
            self.print_statistics()
    
    def print_statistics(self):
        """Print server statistics"""
        stats = network_bridge.get_statistics()
        
        print(f"\n{'='*70}")
        print(f"📊 SERVER STATISTICS - [{self.server_type} AES]")
        print(f"{'='*70}")
        print(f"  Total Connections:      {self.connection_count}")
        print(f"  Total Bytes Received:   {self.total_bytes_received} bytes")
        print(f"  Total Packets:          {stats['total_packets']}")
        print(f"  Average Latency:        {stats['average_latency_ms']} ms")
        print(f"  Network Latency:        {stats['network_latency_ms']} ms")
        print(f"  Encryption Overhead:    {stats['encryption_overhead_ms']} ms")
        print(f"{'='*70}\n")

if __name__ == "__main__":
    import sys
    
    # Check if --optimized flag is provided
    use_ga = "--optimized" in sys.argv
    
    server = IntegrationServer(
        host='127.0.0.1',
        port=5000,
        use_ga_optimization=use_ga
    )
    server.start()
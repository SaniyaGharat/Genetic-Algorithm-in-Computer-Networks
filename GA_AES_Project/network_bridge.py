"""
Network Bridge - Connects Python encryption to Packet Tracer simulation
Simulates network latency and packet flow tracking
"""

import socket
import json
import time
from datetime import datetime
import threading
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class NetworkPacket:
    """Represents a network packet"""
    source_ip: str
    dest_ip: str
    payload: bytes
    timestamp: float
    latency_ms: float
    size_bytes: int

class PacketTracerBridge:
    """
    Bridge between Python encryption and Packet Tracer network simulation
    """
    
    def __init__(self, simulation_enabled=True):
        self.simulation_enabled = simulation_enabled
        self.packets_sent = []
        self.packets_received = []
        self.statistics = {
            'total_packets': 0,
            'total_bytes': 0,
            'total_latency': 0,
            'encryption_overhead': 0,
            'network_latency': 0
        }
        
    def simulate_network_latency(self, packet_size_bytes: int, 
                                 is_encrypted: bool = True) -> float:
        """
        Simulate network latency based on packet size
        (Packet Tracer would measure this)
        
        Args:
            packet_size_bytes: Size of packet to send
            is_encrypted: Whether packet is encrypted
            
        Returns:
            Simulated latency in milliseconds
        """
        
        # Base network latency (from Packet Tracer simulation)
        base_latency = 2.0  # ms (you can measure this in Packet Tracer)
        
        # Latency increases with packet size (network effect)
        size_latency = (packet_size_bytes / 1000) * 0.5  # 0.5ms per KB
        
        # Encryption adds overhead
        encryption_overhead = 0.42 if is_encrypted else 0  # ms
        
        total_latency = base_latency + size_latency + encryption_overhead
        
        self.statistics['network_latency'] += base_latency
        self.statistics['encryption_overhead'] += encryption_overhead
        
        return total_latency
    
    def send_packet(self, source_ip: str, dest_ip: str, 
                   payload: bytes, encryption_type: str = "GA-AES") -> NetworkPacket:
        """
        Send a packet through simulated network
        
        Args:
            source_ip: Source IP address
            dest_ip: Destination IP address
            payload: Data being sent
            encryption_type: Type of encryption used
            
        Returns:
            NetworkPacket object with latency data
        """
        
        timestamp = time.time()
        packet_size = len(payload)
        
        # Simulate network latency
        is_encrypted = encryption_type != "PLAIN"
        latency = self.simulate_network_latency(packet_size, is_encrypted)
        
        # Create packet object
        packet = NetworkPacket(
            source_ip=source_ip,
            dest_ip=dest_ip,
            payload=payload,
            timestamp=timestamp,
            latency_ms=latency,
            size_bytes=packet_size
        )
        
        self.packets_sent.append(packet)
        self.statistics['total_packets'] += 1
        self.statistics['total_bytes'] += packet_size
        self.statistics['total_latency'] += latency
        
        return packet
    
    def receive_packet(self, packet: NetworkPacket) -> NetworkPacket:
        """
        Receive a packet through simulated network
        """
        self.packets_received.append(packet)
        return packet
    
    def get_statistics(self) -> Dict:
        """Get network statistics"""
        if self.statistics['total_packets'] > 0:
            avg_latency = (self.statistics['total_latency'] / 
                          self.statistics['total_packets'])
        else:
            avg_latency = 0
        
        return {
            'total_packets': self.statistics['total_packets'],
            'total_bytes': self.statistics['total_bytes'],
            'average_latency_ms': round(avg_latency, 4),
            'total_latency_ms': round(self.statistics['total_latency'], 2),
            'encryption_overhead_ms': round(self.statistics['encryption_overhead'], 4),
            'network_latency_ms': round(self.statistics['network_latency'], 2)
        }
    
    def print_packet_trace(self, packet: NetworkPacket):
        """Print packet details for debugging"""
        print(f"\n{'='*70}")
        print(f"📦 PACKET TRACE")
        print(f"{'='*70}")
        print(f"  Source IP:        {packet.source_ip}")
        print(f"  Destination IP:   {packet.dest_ip}")
        print(f"  Payload Size:     {packet.size_bytes} bytes")
        print(f"  Network Latency:  {packet.latency_ms:.4f} ms")
        print(f"  Timestamp:        {datetime.fromtimestamp(packet.timestamp)}")
        print(f"{'='*70}\n")

# Global bridge instance
network_bridge = PacketTracerBridge(simulation_enabled=True)
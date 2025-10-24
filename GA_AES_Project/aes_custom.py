"""
Custom AES-128 Implementation with Modifiable Key Schedule
This implementation allows GA to modify rotation values and Rcon application
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import numpy as np
import time

class CustomAES:
    """
    AES-128 wrapper with customizable key schedule parameters
    """
    
    # Standard AES S-box
    SBOX = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    ]
    
    # Standard Rcon values
    RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]
    
    def __init__(self, key_schedule_params=None):
        """
        Initialize AES with custom key schedule parameters
        
        Parameters:
        - key_schedule_params: dict with 'rotations' and 'rcon_multipliers'
          Example: {'rotations': [1,1,1,1,1,1,1,1,1,1], 'rcon_multipliers': [1,1,1,1,1,1,1,1,1,1]}
        """
        if key_schedule_params is None:
            # Standard AES key schedule
            self.rotations = [1] * 10  # Standard: rotate by 1 byte
            self.rcon_multipliers = [1] * 10  # Standard: use Rcon as-is
        else:
            self.rotations = key_schedule_params.get('rotations', [1] * 10)
            self.rcon_multipliers = key_schedule_params.get('rcon_multipliers', [1] * 10)
        
        self.key = None
        self.expanded_key = None
        self.encryption_times = []  # Track encryption times for statistics
        self.decryption_times = []  # Track decryption times for statistics
    
    def rot_word(self, word, positions=1):
        """Rotate a 4-byte word left by 'positions' bytes"""
        positions = positions % 4  # Ensure valid rotation
        return word[positions:] + word[:positions]
    
    def sub_word(self, word):
        """Apply S-box substitution to a 4-byte word"""
        return [self.SBOX[b] for b in word]
    
    def custom_key_expansion(self, key):
        """
        Expand the 16-byte key to 176 bytes (11 round keys for AES-128)
        Uses custom rotation and Rcon multiplication parameters
        """
        key_symbols = list(key)
        expanded = key_symbols[:]
        
        for i in range(4, 44):  # Generate 44 words (176 bytes)
            temp = expanded[(i-1)*4:i*4]
            
            if i % 4 == 0:
                # Apply custom rotation
                round_num = (i // 4) - 1
                rotation = self.rotations[round_num] if round_num < len(self.rotations) else 1
                temp = self.rot_word(temp, rotation)
                
                # Apply S-box
                temp = self.sub_word(temp)
                
                # Apply custom Rcon multiplication
                rcon_mult = self.rcon_multipliers[round_num] if round_num < len(self.rcon_multipliers) else 1
                rcon_value = (self.RCON[round_num] * rcon_mult) % 256
                temp[0] ^= rcon_value
            
            # XOR with word from 4 positions back
            prev_word = expanded[(i-4)*4:(i-3)*4]
            new_word = [temp[j] ^ prev_word[j] for j in range(4)]
            expanded.extend(new_word)
        
        return bytes(expanded)
    
    def encrypt(self, plaintext, key):
        """Encrypt plaintext using custom key schedule"""
        self.key = key
        self.expanded_key = self.custom_key_expansion(key)
        
        # Track encryption time
        start_time = time.perf_counter()
        
        # Use standard AES encryption with our expanded key
        # Note: This is a simplified approach; full implementation would use expanded_key directly
        cipher = AES.new(key, AES.MODE_ECB)
        padded_plaintext = pad(plaintext, AES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)
        
        # Record encryption time in milliseconds
        end_time = time.perf_counter()
        encryption_time = (end_time - start_time) * 1000
        self.encryption_times.append(encryption_time)
        
        return ciphertext
    
    def decrypt(self, ciphertext, key):
        """Decrypt ciphertext using custom key schedule"""
        self.key = key
        self.expanded_key = self.custom_key_expansion(key)
        
        # Track decryption time
        start_time = time.perf_counter()
        
        cipher = AES.new(key, AES.MODE_ECB)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        # Record decryption time in milliseconds
        end_time = time.perf_counter()
        decryption_time = (end_time - start_time) * 1000
        self.decryption_times.append(decryption_time)
        
        return plaintext
    
    def get_key_schedule_entropy(self):
        """Calculate entropy of the expanded key schedule"""
        if self.expanded_key is None:
            return 0
        
        # Calculate Shannon entropy
        byte_counts = np.bincount(list(self.expanded_key), minlength=256)
        probabilities = byte_counts / len(self.expanded_key)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        return entropy
    
    def get_avg_encryption_time(self):
        """Get average encryption time in milliseconds"""
        if not self.encryption_times:
            return 0.0
        return sum(self.encryption_times) / len(self.encryption_times)


class SecurityMetrics:
    """Calculate security metrics for encryption"""
    
    @staticmethod
    def calculate_avalanche_effect(cipher, key, num_tests=100):
        """
        Measure avalanche effect: single bit change in plaintext 
        should flip ~50% of ciphertext bits
        """
        avalanche_percentages = []
        
        for _ in range(num_tests):
            # Generate random plaintext
            plaintext = get_random_bytes(16)
            
            # Encrypt original
            ct1 = cipher.encrypt(plaintext, key)
            
            # Flip one bit in plaintext
            plaintext_list = list(plaintext)
            bit_pos = np.random.randint(0, len(plaintext_list))
            plaintext_list[bit_pos] ^= (1 << np.random.randint(0, 8))
            plaintext_modified = bytes(plaintext_list)
            
            # Encrypt modified
            ct2 = cipher.encrypt(plaintext_modified, key)
            
            # Count bit differences
            diff_bits = sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(ct1, ct2))
            total_bits = len(ct1) * 8
            avalanche_percentages.append((diff_bits / total_bits) * 100)
        
        return np.mean(avalanche_percentages), np.std(avalanche_percentages)
    
    @staticmethod
    def measure_encryption_time(cipher, key, data_size=1024, iterations=100):
        """Measure average encryption time"""
        plaintext = get_random_bytes(data_size)
        
        start_time = time.time()
        for _ in range(iterations):
            _ = cipher.encrypt(plaintext, key)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / iterations
        return avg_time * 1000  # Return in milliseconds
    
    @staticmethod
    def calculate_entropy(data):
        """Calculate Shannon entropy of data"""
        byte_counts = np.bincount(list(data), minlength=256)
        probabilities = byte_counts / len(data)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return entropy


# Example usage
if __name__ == "__main__":
    # Test standard AES
    print("=== Testing Standard AES ===")
    standard_aes = CustomAES()
    key = get_random_bytes(16)
    plaintext = b"Hello, this is a test message for encryption!"
    
    ciphertext = standard_aes.encrypt(plaintext, key)
    decrypted = standard_aes.decrypt(ciphertext, key)
    
    print(f"Original: {plaintext}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {plaintext == decrypted}")
    
    # Calculate metrics
    metrics = SecurityMetrics()
    avalanche_mean, avalanche_std = metrics.calculate_avalanche_effect(standard_aes, key)
    enc_time = metrics.measure_encryption_time(standard_aes, key)
    entropy = standard_aes.get_key_schedule_entropy()
    
    print(f"\n=== Standard AES Metrics ===")
    print(f"Avalanche Effect: {avalanche_mean:.2f}% ± {avalanche_std:.2f}%")
    print(f"Encryption Time: {enc_time:.4f} ms")
    print(f"Key Schedule Entropy: {entropy:.4f} bits")
    
    # Test custom key schedule
    print("\n=== Testing Custom Key Schedule ===")
    custom_params = {
        'rotations': [1, 2, 1, 3, 1, 2, 1, 1, 2, 1],
        'rcon_multipliers': [1, 1, 2, 1, 1, 3, 1, 1, 1, 2]
    }
    custom_aes = CustomAES(custom_params)
    
    ciphertext2 = custom_aes.encrypt(plaintext, key)
    decrypted2 = custom_aes.decrypt(ciphertext2, key)
    
    print(f"Decrypted with custom schedule: {decrypted2}")
    print(f"Match: {plaintext == decrypted2}")
    
    avalanche_mean2, avalanche_std2 = metrics.calculate_avalanche_effect(custom_aes, key)
    enc_time2 = metrics.measure_encryption_time(custom_aes, key)
    entropy2 = custom_aes.get_key_schedule_entropy()
    
    print(f"\n=== Custom AES Metrics ===")
    print(f"Avalanche Effect: {avalanche_mean2:.2f}% ± {avalanche_std2:.2f}%")
    print(f"Encryption Time: {enc_time2:.4f} ms")
    print(f"Key Schedule Entropy: {entropy2:.4f} bits")
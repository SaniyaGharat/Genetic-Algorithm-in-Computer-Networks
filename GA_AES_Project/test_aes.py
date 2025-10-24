# test_aes.py
from aes_custom import CustomAES, SecurityMetrics
from Crypto.Random import get_random_bytes

# Create standard AES
aes = CustomAES()
key = get_random_bytes(16)
plaintext = b"Hello World!"

# Encrypt and decrypt
ciphertext = aes.encrypt(plaintext, key)
decrypted = aes.decrypt(ciphertext, key)

print(f"Original: {plaintext}")
print(f"Decrypted: {decrypted}")
print(f"Success: {plaintext == decrypted}")

# Calculate metrics
metrics = SecurityMetrics()
avalanche = metrics.calculate_avalanche_effect(aes, key, 50)
print(f"Avalanche Effect: {avalanche[0]:.2f}%")
"""
Signing Service
Simple RSA signing and verification operations
"""

import hashlib
import secrets
import math
from base64 import b64encode, b64decode


class SigningService:
    """Simple service for RSA signing and verification operations"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self._generate_key_pair()
    
    def _is_prime(self, n: int, k: int = 5) -> bool:
        """Miller-Rabin primality test"""
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
        
        # Write n-1 as d * 2^r
        r = 0
        d = n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        # Witness loop
        for _ in range(k):
            a = secrets.randbelow(n - 3) + 2
            x = pow(a, d, n)
            
            if x == 1 or x == n - 1:
                continue
            
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        
        return True
    
    def _generate_prime(self, bits: int = 512) -> int:
        """Generate a random prime number"""
        while True:
            p = secrets.randbits(bits)
            p |= (1 << bits - 1) | 1  # Set MSB and LSB
            
            if self._is_prime(p):
                return p
    
    def _extended_gcd(self, a: int, b: int) -> tuple:
        """Extended Euclidean Algorithm"""
        if a == 0:
            return b, 0, 1
        
        gcd, x1, y1 = self._extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        
        return gcd, x, y
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """Modular multiplicative inverse"""
        gcd, x, _ = self._extended_gcd(a, m)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        return (x % m + m) % m
    
    def _generate_key_pair(self, key_size: int = 1024):
        """Generate RSA key pair"""
        try:
            # Generate two distinct primes
            p = self._generate_prime(key_size // 2)
            q = self._generate_prime(key_size // 2)
            
            # Ensure p != q
            while p == q:
                q = self._generate_prime(key_size // 2)
            
            # Calculate n and phi(n)
            n = p * q
            phi_n = (p - 1) * (q - 1)
            
            # Choose e (commonly 65537)
            e = 65537
            while math.gcd(e, phi_n) != 1:
                e += 2
            
            # Calculate d (private exponent)
            d = self._mod_inverse(e, phi_n)
            
            # Store keys
            self.public_key = {'n': n, 'e': e}
            self.private_key = {'n': n, 'd': d}
            
        except Exception as e:
            raise Exception(f"Key pair generation failed: {str(e)}")
    
    def _pkcs1_pad(self, message: bytes, key_size: int) -> int:
        """PKCS#1 v1.5 padding for signing"""
        ps_len = key_size - len(message) - 3
        if ps_len < 8:
            raise ValueError("Message too long for key size")
        
        padded = b'\x00\x01' + b'\xff' * ps_len + b'\x00' + message
        return int.from_bytes(padded, 'big')
    
    def _pkcs1_unpad(self, padded_int: int, key_size: int) -> bytes:
        """Remove PKCS#1 v1.5 padding"""
        padded_bytes = padded_int.to_bytes(key_size, 'big')
        
        if len(padded_bytes) < 11:
            raise ValueError("Invalid padding length")
        
        if padded_bytes[0] != 0x00 or padded_bytes[1] != 0x01:
            raise ValueError("Invalid padding header")
        
        # Find separator (0x00 after 0xFF padding)
        separator_index = None
        for i in range(2, len(padded_bytes)):
            if padded_bytes[i] == 0x00:
                separator_index = i
                break
            elif padded_bytes[i] != 0xFF:
                raise ValueError("Invalid padding")
        
        if separator_index is None or separator_index < 10:
            raise ValueError("Invalid or insufficient padding")
        
        return padded_bytes[separator_index + 1:]
    
    def sign(self, message: str) -> dict:
        """Sign a message using RSA with SHA256"""
        try:
            if not message:
                return {
                    'success': False,
                    'error': 'Message is required for signing'
                }
            
            # Hash the message with SHA256
            hash_obj = hashlib.sha256(message.encode('utf-8'))
            message_hash = hash_obj.digest()
            
            # Get key size in bytes
            key_size = (self.private_key['n'].bit_length() + 7) // 8
            
            # Apply PKCS#1 padding
            padded_hash = self._pkcs1_pad(message_hash, key_size)
            
            # Sign with private key
            signature_int = pow(padded_hash, self.private_key['d'], self.private_key['n'])
            
            # Convert to bytes and encode to base64
            signature_bytes = signature_int.to_bytes(key_size, 'big')
            signature_b64 = b64encode(signature_bytes).decode('utf-8')
            
            # Create public key string for verification
            public_key_data = f"n={hex(self.public_key['n'])[2:]}\ne={hex(self.public_key['e'])[2:]}"
            public_key_pem = f"-----BEGIN CUSTOM RSA PUBLIC KEY-----\n{public_key_data}\n-----END CUSTOM RSA PUBLIC KEY-----"
            
            return {
                'success': True,
                'signature': signature_b64,
                'algorithm': 'SHA256',
                'message': message,
                'public_key': public_key_pem
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Signing failed: {str(e)}'
            }
    
    def verify(self, message: str, signature: str, public_key_pem: str = None) -> dict:
        """Verify a signature using RSA with SHA256"""
        try:
            if not message or not signature:
                return {
                    'success': False,
                    'error': 'Message and signature are required for verification'
                }
            
            # Use internal public key if none provided
            if not public_key_pem:
                public_key_data = f"n={hex(self.public_key['n'])[2:]}\ne={hex(self.public_key['e'])[2:]}"
                public_key_pem = f"-----BEGIN CUSTOM RSA PUBLIC KEY-----\n{public_key_data}\n-----END CUSTOM RSA PUBLIC KEY-----"
            
            # Parse public key
            lines = public_key_pem.strip().split('\n')
            if not (lines[0].startswith('-----BEGIN CUSTOM RSA PUBLIC KEY-----') and 
                    lines[-1].startswith('-----END CUSTOM RSA PUBLIC KEY-----')):
                return {'success': False, 'error': 'Invalid public key format'}
            
            key_data = {}
            for line in lines[1:-1]:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key_data[key] = int(value, 16)
            
            if 'n' not in key_data or 'e' not in key_data:
                return {'success': False, 'error': 'Missing key components'}
            
            # Decode signature
            signature_bytes = b64decode(signature.encode('utf-8'))
            signature_int = int.from_bytes(signature_bytes, 'big')
            
            # Verify signature using RSA public key operation
            key_size = (key_data['n'].bit_length() + 7) // 8
            decrypted_int = pow(signature_int, key_data['e'], key_data['n'])
            
            # Remove padding and get hash
            try:
                decrypted_hash = self._pkcs1_unpad(decrypted_int, key_size)
            except ValueError:
                return {
                    'success': True,
                    'verified': False,
                    'algorithm': 'SHA256',
                    'message': 'Invalid signature padding'
                }
            
            # Calculate expected hash
            expected_hash = hashlib.sha256(message.encode('utf-8')).digest()
            
            # Compare hashes
            is_verified = decrypted_hash == expected_hash
            
            return {
                'success': True,
                'verified': is_verified,
                'algorithm': 'SHA256',
                'message': message,
                'signature': signature
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Verification failed: {str(e)}'
            }


# Create service instance
signing_service = SigningService()
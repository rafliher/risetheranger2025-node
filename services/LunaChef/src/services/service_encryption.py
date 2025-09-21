"""
Encryption Service
Simple encryption and decryption operations
"""

import hashlib
from base64 import b64encode, b64decode


class EncryptionService:
    """Simple service for encryption and decryption operations"""
    
    def __init__(self):
        # Hardcoded XOR key for simple encryption/decryption
        self.XOR_KEY = b'LunaChef2025'
    
    def _xor_operation(self, data: bytes, key: bytes) -> bytes:
        """Simple XOR operation (works for both encrypt and decrypt)"""
        key_len = len(key)
        return bytes(data[i] ^ key[i % key_len] for i in range(len(data)))
    
    def encrypt(self, message: str) -> dict:
        """Encrypt a message using XOR with hardcoded key"""
        try:
            if not message:
                return {
                    'success': False,
                    'error': 'Message is required for encryption'
                }
            
            # Convert message to bytes and encrypt with XOR
            message_bytes = message.encode('utf-8')
            encrypted_bytes = self._xor_operation(message_bytes, self.XOR_KEY)
            
            # Encode to base64 for safe transport
            encrypted_data = b64encode(encrypted_bytes).decode('utf-8')
            
            return {
                'success': True,
                'encrypted_data': encrypted_data,
                'algorithm': 'XOR',
                'message': message
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Encryption failed: {str(e)}'
            }
    
    def decrypt(self, encrypted_data: str) -> dict:
        """Decrypt encrypted data using XOR with hardcoded key"""
        try:
            if not encrypted_data:
                return {
                    'success': False,
                    'error': 'Encrypted data is required for decryption'
                }
            
            # Decode from base64
            encrypted_bytes = b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt with XOR (same operation as encrypt)
            decrypted_bytes = self._xor_operation(encrypted_bytes, self.XOR_KEY)
            
            # Convert back to string
            decrypted_message = decrypted_bytes.decode('utf-8')
            
            return {
                'success': True,
                'decrypted_data': decrypted_message,
                'algorithm': 'XOR',
                'encrypted_data': encrypted_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Decryption failed: {str(e)}'
            }


# Create service instance
encryption_service = EncryptionService()
"""
Encryption Service
"""

from base64 import b64encode, b64decode
from config import key

class EncryptionService:
    def __init__(self):
        self.KEY = key
    
    def _xor_operation(self, data: bytes, key: bytes) -> bytes:
        key_len = len(key)
        return bytes(data[i] ^ key[i % key_len] for i in range(len(data)))
    
    def encrypt(self, message: str) -> dict:
        try:
            if not message:
                return {
                    'success': False,
                    'error': 'Message is required for encryption'
                }
            
            message_bytes = message.encode('utf-8')
            encrypted_bytes = self._xor_operation(message_bytes, self.KEY)
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
        try:
            if not encrypted_data:
                return {
                    'success': False,
                    'error': 'Encrypted data is required for decryption'
                }
            
            encrypted_bytes = b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = self._xor_operation(encrypted_bytes, self.KEY)
            decrypted_message = decrypted_bytes.decode('utf-8')
            
            return {
                'success': True,
                'decrypted_text': decrypted_message,
                'algorithm': 'XOR',
                'encrypted_data': encrypted_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Decryption failed: {str(e)}'
            }

encryption_service = EncryptionService()
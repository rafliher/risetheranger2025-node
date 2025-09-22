"""
Hashing Service

patching_notes:
- keep this line: 
    from config import hash_key
    hashing_service = HashingService()
- keep class base structure and methods:
    class HashingService:
    def hash(self, message: str):
- dont change structure or remote config.py (you can change the values)
- dont change features on application
"""

import hashlib
from config import hash_key

class HashingService:
    def hash(self, message: str):
        try:
            if not message:
                return {
                    'success': False,
                    'error': 'Message is required for hashing'
                }
            message = message.encode('utf-8')
            hash_result = ''
            for i in range(4):
                hash_result += hashlib.sha1(message[len(message) // 4 * i:len(message) // 4 * (i + 1)]).hexdigest()
            
            return {
                'success': True,
                'hash': hash_result,
                'algorithm': 'HASH MAGIC'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Hashing failed: {str(e)}'
            }

hashing_service = HashingService()
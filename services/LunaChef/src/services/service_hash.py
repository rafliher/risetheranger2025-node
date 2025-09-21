"""
Hashing Service
Simple SHA256 hashing operations
"""

import hashlib


class HashingService:
    """Simple service for SHA256 hashing operations"""
    
    def hash(self, message: str):
        """Generate SHA256 hash of the message"""
        try:
            if not message:
                return {
                    'success': False,
                    'error': 'Message is required for hashing'
                }
            
            # Simple SHA256 hash
            hash_obj = hashlib.sha256(message.encode('utf-8'))
            hash_result = hash_obj.hexdigest()
            
            return {
                'success': True,
                'hash': hash_result,
                'algorithm': 'SHA256',
                'message': message
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Hashing failed: {str(e)}'
            }


# Create service instance
hashing_service = HashingService()
"""
Services Package
Contains individual service files for each cryptographic operation
"""
from config import key
from config import hash_key
from config import signing_key

from .service_encryption import EncryptionService
from .service_signing import SigningService
from .service_hash import HashingService

encryption_service = EncryptionService(key)
signing_service = SigningService(4, signing_key)
hashing_service = HashingService(hash_key)
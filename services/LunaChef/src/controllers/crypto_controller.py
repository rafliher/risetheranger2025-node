from flask import Blueprint, render_template, request, jsonify
from services import (
    service_encryption,
    service_signing,
    service_hash
)

# Create blueprint
crypto_bp = Blueprint('crypto', __name__)

# Initialize services
encryption_service = service_encryption.EncryptionService()
signing_service = service_signing.SigningService()
hash_service = service_hash.HashingService()

@crypto_bp.route('/crypto')
def crypto_page():
    """Render the crypto operations page"""
    return render_template('crypto.html')

@crypto_bp.route('/encrypt', methods=['POST'])
def encrypt_text():
    """Encrypt text using simplified service"""
    try:
        text = request.form.get('text', '').strip()
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'})
        
        result = encryption_service.encrypt(text)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crypto_bp.route('/decrypt', methods=['POST'])
def decrypt_text():
    """Decrypt text using simplified service"""
    try:
        encrypted_data = request.form.get('encrypted_data', '').strip()
        
        if not encrypted_data:
            return jsonify({'success': False, 'error': 'Encrypted data is required'})
        
        result = encryption_service.decrypt(encrypted_data)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crypto_bp.route('/sign', methods=['POST'])
def sign_data():
    """Sign data using simplified service"""
    try:
        data = request.form.get('data', '').strip()
        
        if not data:
            return jsonify({'success': False, 'error': 'Data is required'})
        
        result = signing_service.sign(data)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crypto_bp.route('/verify', methods=['POST'])
def verify_signature():
    """Verify signature using simplified service"""
    try:
        data = request.form.get('data', '').strip()
        signature = request.form.get('signature', '').strip()
        
        if not all([data, signature]):
            return jsonify({'success': False, 'error': 'Data and signature are required'})
        
        # Use the updated verify method with hex signature
        result = signing_service.verify(signature, data)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@crypto_bp.route('/hash', methods=['POST'])
def hash_data():
    """Generate hash of data"""
    try:
        data = request.form.get('data', '').strip()
        
        if not data:
            return jsonify({'success': False, 'error': 'Data is required'})
        
        result = hash_service.hash(data)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
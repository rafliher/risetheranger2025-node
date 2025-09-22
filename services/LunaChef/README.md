# LunaChef Crypto Web Application

A comprehensive Python web application for cryptographic operations including encryption/decryption, digital signatures, and hashing. **All cryptographic algorithms are implemented natively in Python without external crypto libraries.**

## Features

- **🔐 Encryption/Decryption**: Multiple native algorithms (XOR, Caesar, Vigenère, Block Cipher) with PBKDF2 key derivation
- **✍️ Digital Signatures**: Native RSA implementation for data authentication and integrity
- **🧩 Hashing**: Multiple native algorithms (MD5, SHA1, SHA256, SHA512, BLAKE2b) with HMAC support
- **🎨 Modern UI**: Bootstrap-based responsive web interface
- **🐳 Docker Support**: Easy deployment with Docker and Docker Compose
- **🛡️ Native Implementation**: All crypto algorithms implemented using only Python standard library

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd risetheranger2025-node/services/LunaChef
   ```

2. **Start the application**
   ```bash
   # For production
   docker-compose up -d
   
   # For development (with hot reload)
   docker-compose -f docker-compose.dev.yml up -d
   
   # Using the start script
   chmod +x start.sh
   ./start.sh prod    # or ./start.sh dev
   ```

3. **Access the application**
   - Open your browser and go to: http://localhost:5000

### Manual Installation

1. **Install Python dependencies**
   ```bash
   cd src
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python main.py
   ```

## Usage

### Encryption/Decryption
- Enter text to encrypt or upload a file
- Optional: Use a password for key derivation
- Copy the encrypted data and key/salt for later decryption

### Digital Signatures
- Sign data with automatically generated RSA keys
- Verify signatures using the original data, signature, and public key

### Hashing
- Generate hash values using MD5, SHA1, SHA256, or SHA512
- Support for both text input and file content

### File Operations
- Upload files (TXT, PDF, PNG, JPG, JPEG, GIF, DOC, DOCX)
- Use file content in any crypto operation
- Persistent file storage across container restarts

## Docker Commands

```bash
# Start production environment
docker-compose up -d

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# Using the start script
./start.sh dev      # Development mode
./start.sh prod     # Production mode
./start.sh stop     # Stop all containers
./start.sh logs     # View logs
./start.sh rebuild  # Rebuild containers
```

## Architecture

The application follows the Model-View-Controller (MVC) pattern with a dedicated service layer:

```
src/
├── main.py                 # Flask application entry point
├── models/                # Data models (currently empty)
├── services/              # Individual service files for crypto operations
│   ├── encryption_service.py # Encryption operations
│   ├── decryption_service.py # Decryption operations
│   ├── signing_service.py    # Digital signing operations
│   ├── verification_service.py # Signature verification operations
│   └── hashing_service.py    # Hashing operations
├── controllers/
│   └── crypto_controller.py # Request handling and routing
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   └── crypto.html        # Crypto operations page
├── static/
│   └── style.css          # Custom styles
└── requirements.txt       # Python dependencies
```

### Service Layer Architecture

Each cryptographic operation is handled by a dedicated service with **native Python implementations**:

- **`service_encrypt.py`**: Native encryption algorithms
  - XOR cipher with key expansion
  - Caesar cipher with configurable shift
  - Vigenère cipher with repeating key
  - Simple block cipher with padding
  - PBKDF2 key derivation using hashlib
  - Base64 encoding for output

- **`service_decrypt.py`**: Native decryption algorithms
  - Automatic algorithm detection
  - XOR, Caesar, Vigenère, block cipher decryption
  - PBKDF2 key derivation for decryption
  - Input validation and error handling

- **`service_sign.py`**: Native RSA digital signing
  - Miller-Rabin primality testing
  - RSA key pair generation (1024-4096 bits)
  - PKCS#1 v1.5 padding implementation
  - SHA256, SHA512, MD5 signature algorithms
  - Custom PEM format for key storage

- **`service_verify.py`**: Native RSA signature verification
  - RSA public key operations
  - PKCS#1 v1.5 padding verification
  - Multi-algorithm verification support
  - Auto-detection of signature algorithms
  - Custom PEM key parsing

- **`service_hash.py`**: Native hashing operations
  - Multiple algorithms: MD5, SHA1, SHA256, SHA512, BLAKE2b/s
  - HMAC generation and verification using hmac module
  - PBKDF2 and scrypt key derivation
  - Salt generation with secrets module
  - Timing-safe hash comparison

## Native Implementation Details

This application uses **only Python standard library** for all cryptographic operations:

### Standard Library Modules Used
- `hashlib`: SHA, MD5, BLAKE2 hashing algorithms
- `hmac`: Hash-based Message Authentication Code
- `secrets`: Cryptographically secure random number generation
- `base64`: Base64 encoding/decoding
- `math`: Mathematical operations for prime generation
- `os`: Operating system interface

### No External Dependencies
- ❌ No `cryptography` library
- ❌ No `pycryptodome` library  
- ❌ No external crypto packages
- ✅ Pure Python implementation
- ✅ Educational and transparent code

## Security Features

- Input validation and sanitization
- Secure file upload handling
- RSA key pair generation for signing
- Password-based key derivation (PBKDF2)
- Non-root container user
- Health checks for container monitoring

## Development

### Environment Variables

- `FLASK_ENV`: Set to `development` for debug mode
- `FLASK_DEBUG`: Enable Flask debug mode
- `SECRET_KEY`: Flask secret key (change in production)

### File Structure

- `Dockerfile`: Production container configuration
- `docker-compose.yml`: Production deployment
- `docker-compose.dev.yml`: Development environment
- `.dockerignore`: Files to exclude from Docker build
- `start.sh`: Convenience script for container management

## Supported File Types

- Text files: `.txt`
- Documents: `.pdf`, `.doc`, `.docx`
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`

## API Endpoints

### Core Operations
- `GET /`: Home page
- `GET /crypto`: Crypto operations page
- `POST /upload`: Upload file
- `GET /files`: List uploaded files
- `GET /file/<filename>`: Get file content

### Encryption & Decryption
- `POST /encrypt`: Encrypt text
- `POST /decrypt`: Decrypt text
- `POST /generate-key`: Generate Fernet key

### Digital Signatures
- `POST /sign`: Sign data
- `POST /verify`: Verify signature
- `GET /key-info`: Get RSA key information
- `POST /regenerate-keys`: Generate new RSA key pair

### Hashing
- `POST /hash`: Generate hash
- `POST /hash-multiple`: Hash with multiple algorithms
- `POST /hmac-generate`: Generate HMAC
- `POST /hmac-verify`: Verify HMAC
- `POST /generate-salt`: Generate random salt

### File Operations
- `POST /file-encrypt/<filename>`: Encrypt file content
- `POST /file-hash/<filename>`: Hash file content
- `POST /file-sign/<filename>`: Sign file content

### Utility
- `GET /algorithms`: Get supported algorithms

## Testing

Run the service test suite:
```bash
# Test individual services
python test_services.py

# Or run from Docker container
docker-compose exec lunachef-crypto-app python test_services.py
```

## License

This project is part of the Rise the Ranger 2025 CTF challenge.

## Troubleshooting

### Container Issues
```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs -f lunachef-crypto-app

# Restart containers
docker-compose restart
```

### Permission Issues
```bash
# Fix file permissions
chmod +x start.sh
```

### Port Conflicts
If port 5000 is already in use, modify the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Change 5000 to any available port
```
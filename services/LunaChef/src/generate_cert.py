#!/usr/bin/env python3
"""
Script to generate self-signed SSL certificates for LunaChef HTTPS server
"""

import os
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

def generate_self_signed_cert(hostname="localhost", cert_dir="certs"):
    """Generate self-signed certificate and private key"""
    
    # Create certs directory if it doesn't exist
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate subject
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "ID"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Jakarta"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Jakarta"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "LunaChef"),
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ])
    
    # Create certificate
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # Valid for 1 year
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(hostname),
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Write private key to file
    key_path = os.path.join(cert_dir, "server.key")
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Write certificate to file
    cert_path = os.path.join(cert_dir, "server.crt")
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print(f"✅ Self-signed certificate generated successfully!")
    print(f"📁 Certificate: {cert_path}")
    print(f"🔑 Private Key: {key_path}")
    print(f"🌐 Hostname: {hostname}")
    print(f"⏰ Valid for: 1 year")
    
    return cert_path, key_path

if __name__ == "__main__":
    import argparse
    import ipaddress
    
    parser = argparse.ArgumentParser(description="Generate self-signed SSL certificate for LunaChef")
    parser.add_argument("--hostname", default="localhost", help="Hostname for certificate (default: localhost)")
    parser.add_argument("--cert-dir", default="certs", help="Directory to store certificates (default: certs)")
    
    args = parser.parse_args()
    
    try:
        generate_self_signed_cert(args.hostname, args.cert_dir)
    except Exception as e:
        print(f"❌ Error generating certificate: {e}")
        exit(1)
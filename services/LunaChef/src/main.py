from flask import Flask, render_template, send_from_directory
import os
import ssl
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env files"""
    # Load base .env file
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    
    # Load environment-specific .env file
    flask_env = os.getenv('FLASK_ENV', 'development')
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'.env.{flask_env}')
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)

def str_to_bool(value):
    """Convert string to boolean"""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ('true', '1', 'yes', 'on')

def create_app():
    # Load environment configuration
    load_environment()
    
    app = Flask(__name__)
    
    # Basic Flask configuration from environment
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'lunachef-fallback-secret-key')
    
    # Register controllers
    from controllers.crypto_controller import crypto_bp
    app.register_blueprint(crypto_bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/scripts')
    def view_scripts():
        return render_template('scripts.html')
    
    @app.route('/scripts/<service_name>')
    def view_service_script(service_name):
        """View the source code of a specific service"""
        try:
            # Validate service name to prevent path traversal
            allowed_services = ['encryption', 'signing', 'hash']
            if service_name not in allowed_services:
                return render_template('error.html', 
                                     error_title="🌫️ Service Not Found",
                                     error_message=f"The requested service '{service_name}' does not exist in Luna's spellbook."), 404
            
            service_file = os.path.join(os.path.dirname(__file__), 'services', f'service_{service_name}.py')
            
            if not os.path.exists(service_file):
                return render_template('error.html',
                                     error_title="📜 Scroll Missing",
                                     error_message=f"The sacred scroll for '{service_name}' could not be found."), 404
            
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return render_template('script_viewer.html', 
                                 service_name=service_name, 
                                 content=content)
                                 
        except FileNotFoundError:
            return render_template('error.html',
                                 error_title="📜 Scroll Missing", 
                                 error_message=f"The sacred scroll for '{service_name}' has vanished from Luna's library."), 404
        except PermissionError:
            return render_template('error.html',
                                 error_title="🔒 Access Forbidden",
                                 error_message="Luna's protective wards prevent access to this sacred knowledge."), 403
        except Exception as e:
            return render_template('error.html',
                                 error_title="🌙 Mystical Error",
                                 error_message=f"An unexpected magical disturbance occurred: {str(e)}"), 500
    
    @app.route('/backsound/<filename>')
    def serve_audio(filename):
        """Serve audio files from the backsound directory"""
        try:
            backsound_dir = os.path.join(os.path.dirname(__file__), 'backsound')
            return send_from_directory(backsound_dir, filename)
        except Exception as e:
            return f"Audio file not found: {str(e)}", 404
    
    return app

def setup_ssl_context():
    """Setup SSL context for HTTPS"""
    cert_dir = os.path.join(os.path.dirname(__file__), 'certs')
    cert_file = os.path.join(cert_dir, 'server.crt')
    key_file = os.path.join(cert_dir, 'server.key')
    
    # Check if certificates exist
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("🔒 SSL certificates not found. Generating self-signed certificates...")
        try:
            from generate_cert import generate_self_signed_cert
            generate_self_signed_cert(cert_dir=cert_dir)
        except ImportError:
            print("❌ Could not import certificate generator. Please run generate_cert.py first.")
            return None
        except Exception as e:
            print(f"❌ Error generating certificates: {e}")
            return None
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(cert_file, key_file)
    return context

if __name__ == '__main__':
    app = create_app()
    debug_mode = str_to_bool(os.getenv('FLASK_DEBUG', 'false'))
    
    # SSL/HTTPS configuration
    use_https = str_to_bool(os.getenv('USE_HTTPS', 'false'))
    # use_https = str_to_bool(os.getenv('USE_HTTPS', 'true'))
    
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    if use_https:
        ssl_context = setup_ssl_context()
        if ssl_context:
            print(f"🌙 LunaChef server starting with HTTPS on https://{host}:{port}")
            print("🔒 Using self-signed certificate (browsers will show security warning)")
            app.run(debug=debug_mode, host=host, port=port, ssl_context=ssl_context)
        else:
            print("⚠️  SSL setup failed, falling back to HTTP")
            print(f"🌙 LunaChef server starting with HTTP on http://{host}:{port}")
            app.run(debug=debug_mode, host=host, port=port)
    else:
        print(f"🌙 LunaChef server starting with HTTP on http://{host}:{port}")
        app.run(debug=debug_mode, host=host, port=port)
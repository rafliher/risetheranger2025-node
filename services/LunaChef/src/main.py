from flask import Flask, render_template, send_from_directory
import os
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

if __name__ == '__main__':
    app = create_app()
    debug_mode = str_to_bool(os.getenv('FLASK_DEBUG', 'false'))
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
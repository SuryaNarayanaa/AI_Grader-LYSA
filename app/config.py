import os
from flask import Flask

def configure_app(app: Flask):
   # Secret key for session management
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # File upload configurations
    app.config['uploads'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    
    # Ensure upload directories exist
    os.makedirs(app.config['uploads'], exist_ok=True)
    
    # Other application configurations
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}
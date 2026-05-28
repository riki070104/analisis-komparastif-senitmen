import os
from flask import Flask
from .extensions import db, login_manager

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Konfigurasi Koneksi Database ke MySQL Laragon
    # Username default: root, Password kosong, Database: sentiment_app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@127.0.0.1/sentiment_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import models (harus diimpor agar SQLAlchemy mengenali tabel-tabelnya)
    from .models import User, Dataset
    
    # Register blueprints
    from .auth import auth_bp
    from .routes import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # Create tables automatically
    with app.app_context():
        db.create_all()
    
    return app

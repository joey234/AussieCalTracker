from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from app.routes import auth_bp, main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Ensure the upload folder exists
    import os
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

# Import models here to avoid circular imports
from app.models import User, FoodEntry

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 
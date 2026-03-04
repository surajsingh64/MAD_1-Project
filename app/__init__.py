from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)

    # Import Blueprints
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.student import student_bp
    from app.company import company_bp

    # Register Blueprints with URL Prefix
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(company_bp, url_prefix="/company")

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

    # Create tables and default admin
    with app.app_context():
        from app import models
        db.create_all()
        create_admin()

    return app


def create_admin():
    from app.models import User

    existing_admin = User.query.filter_by(
        email="singhsuraj817844@gmail.com"
    ).first()

    if existing_admin:
        print("Admin already exists. Skipping creation.")
    else:
        print("Creating new admin...")

        admin = User(
            email="singhsuraj817844@gmail.com",
            password=generate_password_hash("admin@5129"),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
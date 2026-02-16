from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()

 
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from app import models
        db.create_all()
        create_admin()
    return app

def create_admin():
    from app.models import User

    if not User.query.filter_by(role='admin').first():
        admin  = User(
            email = "prashantjinwal888@gmail.com",
            password = generate_password_hash("admin@5120"),
            role = "admin"
        )
        db.session.add(admin)
        db.session.commit()

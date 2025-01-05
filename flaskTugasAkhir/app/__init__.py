from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Inisialisasi ekstensi
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'd499d76f79eb146d82fb3cb212f3b55a64095509e820d6aa'
    app.config.from_object('app.config.Config')

    # Inisialisasi ekstensi dengan aplikasi Flask
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Daftarkan blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app
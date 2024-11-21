from flask import Flask
from .config import Config
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    from .routes import main

    app.register_blueprint(main)

    from app.db import db, create_initial_values

    db.init_app(app)
    Migrate(app, db)
    with app.app_context():
        db.create_all()
        create_initial_values()

    return app

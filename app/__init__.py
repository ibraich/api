from flask import Flask
from dotenv import load_dotenv

from flask_migrate import Migrate


def create_app(config_class):
    app = Flask(__name__)
    load_dotenv()
    app.config.from_object(config_class)

    # Register blueprints
    from .routes import main, project

    app.register_blueprint(main)

    if not config_class.TESTING:
        from app.db import db

        db.init_app(app)
        Migrate(app, db)
        with app.app_context():
            db.create_all()

    return app

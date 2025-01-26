from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.config import Config

db = SQLAlchemy()


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)


def add_transaction_wrapper(app: Flask):
    # Transaction management
    @app.before_request
    def start_transaction():
        """Start a session and a transaction before each request."""
        g.db_session = Session()
        g.db_session.begin()

    @app.after_request
    def commit_or_rollback_transaction(response):
        """Commit the transaction or rollback in case of an error after the request."""
        try:
            if response.status_code < 400:  # Commit only for successful responses
                g.db_session.commit()
            else:
                g.db_session.rollback()
        except Exception as e:
            g.db_session.rollback()
            raise e
        finally:
            Session.remove()  # Remove the session after request

        return response

    @app.teardown_appcontext
    def tear_down_exception(exception=None):
        """Clean up the session when the application context is torn down."""
        if hasattr(g, "db_session"):
            Session.remove()

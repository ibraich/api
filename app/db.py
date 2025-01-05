from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.config import Config

db = SQLAlchemy()


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

from functools import wraps


def transactional(func):
    """
    Decorator to wrap a function in a database transaction.
    Ensures commit/rollback and proper session cleanup.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Start a transaction
            with Session.begin():  # Automatically commits
                result = func(*args, **kwargs)
            print("Transaction committed.")
            return result
        except Exception as e:
            Session.rollback()  # Explicit rollback if needed
            raise e
        finally:
            Session.remove()  # Remove the session from the scope

    return wrapper

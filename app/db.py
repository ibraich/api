from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.exceptions import HTTPException, InternalServerError

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
            return result
        except HTTPException as e:  # Reraise HTTP Exceptions
            Session.rollback()  # Explicit rollback if needed
            raise e
        except Exception as e:  # Raise Internal Server Error on any other exception
            Session.rollback()  # Explicit rollback if needed
            raise InternalServerError(str(e))
        finally:
            Session.remove()  # Remove the session from the scope

    return wrapper

import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    DEBUG = os.getenv("DEBUG", True)  # Set to False in production

    # Add database configuration here 
    
import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    DEBUG = os.getenv("DEBUG", True)  # Set to False in production
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://user:s3cr3t@host.docker.internal:5432/annotation_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DatabaseEnumConfig:
    document_states = ["NEW", "IN_PROGRESS", "FINISHED"]
    document_edit_states = ["MENTIONS", "ENTITIES", "RELATIONS", "FINISHED"]
    modelling_languages = ["BPMN"]

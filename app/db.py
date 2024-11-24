from flask_sqlalchemy import SQLAlchemy
from app.config import DatabaseEnumConfig

db = SQLAlchemy()


def create_initial_values():
    from app.models import (
        insert_default_values,
        DocumentEditState,
        DocumentState,
        ModellingLanguage,
    )

    insert_default_values(DatabaseEnumConfig.document_states, DocumentState)
    insert_default_values(DatabaseEnumConfig.document_edit_states, DocumentEditState)
    insert_default_values(DatabaseEnumConfig.modelling_languages, ModellingLanguage)

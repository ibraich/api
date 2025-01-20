from app.db import db
from app.models import RecommendationModel
from werkzeug.exceptions import NotFound

class DocumentRecommendationRepository:
    def __init__(self, db):
        self.db = db

    def create(self, recommendation):
        # Store recommendation in the database
        self.db.session.add(recommendation)
        self.db.session.commit()

    def get_by_id(self, recommendation_id):
        # Fetch recommendation by ID
        return self.db.session.query(RecommendationModel).filter_by(id=recommendation_id).first()

    def delete(self, recommendation_id):
        # Delete recommendation by ID
        recommendation = self.get_by_id(recommendation_id)
        if recommendation:
            self.db.session.delete(recommendation)
            self.db.session.commit()

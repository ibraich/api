from app.db import db


class BaseRepository:
    def store_object(self, db_object):
        db.session.add(db_object)
        db.session.commit()

    def get_object_by_id(self, classname, object_id):
        return db.session.query(classname).filter_by(id=object_id).first()

    def get_by_field(self, classname, field, value):
        return (
            db.session.query(classname).filter(getattr(classname, field) == value).all()
        )

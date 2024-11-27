from app.db import db


class BaseRepoisotry:
    @staticmethod
    def store_object(db_object):
        db.session.add(db_object)
        db.session.commit()

    @staticmethod
    def get_object_by_id(classname, object_id):
        return db.session.query(classname).filter_by(id=object_id).first()

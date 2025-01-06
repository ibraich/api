from app.db import db, Session


class BaseRepository:
    def store_object(self, db_object):
        db.session.add(db_object)
        db.session.commit()

    def store_object_transactional(self, db_object):
        Session.add(db_object)
        Session.flush()
        # At this point, the object f has been pushed to the DB,
        # and has been automatically assigned a unique primary key id

        Session.refresh(db_object)
        # refresh updates given object in the session with its state in the DB
        # (and can also only refresh certain attributes - search for documentation)

        return db_object

    def get_object_by_id(self, classname, object_id):
        return db.session.query(classname).filter_by(id=object_id).first()

    def get_by_field(self, classname, field, value):
        return (
            db.session.query(classname).filter(getattr(classname, field) == value).all()
        )

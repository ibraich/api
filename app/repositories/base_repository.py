from flask import g


class BaseRepository:
    def store_object(self, db_object):
        """
        Stores an object in the database
        - The object is pushed to the database and gets an id
        - The object is not committed, as this is done by the transaction wrapper
        :param db_object:
        :return: db_object with all default and auto generated values like id
        """
        self.get_session().add(db_object)
        self.get_session().flush()
        # At this point, the object f has been pushed to the DB,
        # and has been automatically assigned a unique primary key id

        self.get_session().refresh(db_object)
        # refresh updates given object in the session with its state in the DB
        # (and can also only refresh certain attributes - search for documentation)

        return db_object

    def get_object_by_id(self, classname, object_id):
        return self.get_session().query(classname).filter_by(id=object_id).first()

    def get_by_field(self, classname, field, value):
        return (
            self.get_session()
            .query(classname)
            .filter(getattr(classname, field) == value)
            .all()
        )

    def get_session(self):
        return g.db_session

from .config import Config
from sqlalchemy import inspect


class DbEntity():
    session = Config.db_session

    def __init__(self):
        pass

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def save(self):
        self.session.add(self)
        self.session.commit()

    def add(self):
        self.session.add(self)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

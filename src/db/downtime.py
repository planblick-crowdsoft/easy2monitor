from .config import Config
from sqlalchemy import Column, DateTime, Integer, String, Text, Sequence
from db.abstract import DbEntity
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()


class Downtime(DbEntity, Base):
    __tablename__ = 'downtimes'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name_hash = Column(String(255))
    name = Column(String(255))
    seconds = Column(Integer())
    timestamp = Column(DateTime)

    def __init__(self):
        super().__init__()
        Base.metadata.create_all(Config.db_engine)

    def __repr__(self):
        return "<DbPing(name_hash='%s', seconds='%s', timestamp='%s')>" % (self.name_hash, self.seconds, self.timestamp)

    def as_dict(self):
        return {"name_hash": self.name_hash, "data": self.seconds, "timestamp": self.timestamp}

    def save(self):
        try:
            self.session.add(self)
            self.session.commit()
            self.session.flush()
        except Exception as e:
            self.rollback()

    def commit(self):
        self.session.commit()

    def add(self):
        self.session.add(self)

    def rollback(self):
        self.session.rollback(self)

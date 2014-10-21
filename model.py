from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Artist(Base):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    artist_id = Column(ForeignKey('artist.id'))
    name = Column(String)
    count = Column(Integer)
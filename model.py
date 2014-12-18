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


class ArtistVector(Base):
    __tablename__ = 'vector'
    id = Column(Integer, primary_key=True, autoincrement=True)
    artist_id = Column(ForeignKey('artist.id'))
    drum_and_bass = Column(Integer, default=0)
    rock = Column(Integer, default=0)
    punk = Column(Integer, default=0)
    hip_hop = Column(Integer, default=0)
    rap = Column(Integer, default=0)
    dubstep = Column(Integer, default=0)
    electronic = Column(Integer, default=0)
    indie = Column(Integer, default=0)
    soul = Column(Integer, default=0)
    pop = Column(Integer, default=0)
    rnb = Column(Integer, default=0)
    nu_metal = Column(Integer, default=0)
    funk = Column(Integer, default=0)

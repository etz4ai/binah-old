import enum

from pathlib import Path
from sqlalchemy import (Boolean, Column, Date, Float, ForeignKey, Integer,
                        SmallInteger, String, LargeBinary, create_engine)
from sqlalchemy.types import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from binah.util import get_data_home

Base = declarative_base()

def get_config_single_host(initialize=False):
    config = 'sqlite:///' + str(get_data_home() / 'index.db?check_same_thread=False')
    engine = create_engine(config)
    session = sessionmaker(bind=engine)() 
    if initialize:
        Base.metadata.create_all(engine)
    return session

class ControlledImport:
    def __init__(self, session, has_files=False):
        self.home = get_data_home()
        if has_files:
            self.home = self.home / 'images'
        self.home.mkdir(parents=True, exist_ok=True)
        self.session = session

    def exists(self, fname):
        return (self.home / fname).exists()

    def path(self, fname):
        return str(self.home / fname)


class Type(enum.Enum):
    JPEG = 1
    PNG = 2
    GIF = 3
    TIFF = 4
    WEBP = 5
    DBTEXT = 7
    MP4 = 8


class Lifecycle(enum.Enum):
    TRAIN = 1
    TEST = 2
    VERIFY = 3
    FLEXIBLE = 4


class Example(Base):
    __tablename__ = 'examples'
    id = Column(Integer, primary_key=True)
    lifecycle = Column(Enum(Lifecycle), nullable=False)
    type = Column(Enum(Type))
    license_id = Column(SmallInteger, ForeignKey(
        'licenses.id'), nullable=False)
    dataset_id = Column(SmallInteger, ForeignKey(
        'datasets.id'), nullable=False)


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, ForeignKey('examples.id'), primary_key=True)
    src_filename = Column(String)
    url = Column(String)
    orig_url = Column(String)
    captured = Column(Date)


class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, ForeignKey('examples.id'), primary_key=True)
    src_filename = Column(String)
    url = Column(String)
    orig_url = Column(String)
    captured = Column(Date)


class Dataset(Base):
    __tablename__ = 'datasets'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    desc = Column(String)
    url = Column(String)

class Caption(Base):
    __tablename__ = 'captions'
    id = Column(Integer, primary_key=True)
    text_id = Column(Integer, nullable=False)
    image_id = Column(Integer, nullable=False)


class Text(Base):
    __tablename__ = 'texts'
    id = Column(Integer, ForeignKey('examples.id'), primary_key=True)
    text = Column(String)


class BoundingBox(Base):
    __tablename__ = 'boundingboxes'
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    x1 = Column(Float)
    y1 = Column(Float)
    x2 = Column(Float)
    y2 = Column(Float)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    supercategory = Column(String)


class SegmentationCord(Base):
    __tablename__ = 'segmentationcords'
    id = Column(Integer, primary_key=True)
    cord = Column(Float)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False,
                      index=True)


class License(Base):
    __tablename__ = 'licenses'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    name = Column(String)


class Vector(Base):
    __tablename__ = 'vectors'
    id = Column(Integer, ForeignKey('examples.id'), primary_key=True)
    vec = Column(LargeBinary)
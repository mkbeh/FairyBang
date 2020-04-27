# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///fairybang.db')
Base = declarative_base()

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


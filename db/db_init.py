#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal
from db_base import Base

# External
import sqlalchemy
from sqlalchemy import Column, Integer, Float, String, Boolean


class Loader(Base):
    __tablename__ = 'loader'

    entry_id = Column(String, primary_key=True, nullable=False)
    doi = Column(String, nullable=True)

    title = Column(String, nullable=False)
    summary = Column(String, nullable=True)


class Authors(Base):
    __tablename__ = 'authors'

    entry_id = Column(String, primary_key=True, nullable=False)

    author = Column(String, nullable=False)


class Categories(Base):
    __tablename__ = 'categories'

    entry_id = Column(String, primary_key=True, nullable=False)

    category = Column(String, nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)

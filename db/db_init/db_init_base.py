#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal

# External
import sqlalchemy
from sqlalchemy import Column, Integer, Float, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

BaseBase = declarative_base()
base_name = 'base.db'


class Articles(BaseBase):
    __tablename__ = 'base_articles'

    entry_id = Column(String, primary_key=True, nullable=False)

    title = Column(String, nullable=False)
    summary = Column(String, nullable=True)


class Authors(BaseBase):
    __tablename__ = 'base_authors'

    id = Column(Integer, primary_key=True, autoincrement=True)

    entry_id = Column(String, nullable=False)
    author = Column(String, nullable=False)


class Categories(BaseBase):
    __tablename__ = 'base_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)

    entry_id = Column(String, nullable=False)

    primary_category = Column(Integer, nullable=False)
    category = Column(Integer, nullable=False)

    is_primary = Column(Boolean, nullable=False, default=False)


class BaseList(BaseBase):
    __tablename__ = 'cat_base'

    id = Column(Integer, primary_key=True, autoincrement=True)
    base_category = Column(String, nullable=False)


class CatList(BaseBase):
    __tablename__ = 'cat_list'

    id = Column(Integer, primary_key=True, autoincrement=True)
    base_id = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)

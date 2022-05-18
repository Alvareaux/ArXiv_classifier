#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal

# External
from sqlalchemy import ForeignKey, Column, Integer, Float, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

BaseBase = declarative_base()
base_name = 'base.db'


class Articles(BaseBase):
    __tablename__ = 'base_articles'

    entry_id = Column(String(30), primary_key=True, nullable=False)

    title = Column(String(1000), nullable=False)
    summary = Column(String(10000), nullable=True)

    children_base_authors = relationship('Authors')
    children_base_categories = relationship('Categories')


class Authors(BaseBase):
    __tablename__ = 'base_authors'

    id = Column(Integer, primary_key=True, autoincrement=True)

    entry_id = Column(String(30), ForeignKey('base_articles.entry_id'), nullable=False)
    author = Column(String(1000), nullable=False)


class Categories(BaseBase):
    __tablename__ = 'base_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)

    entry_id = Column(String(30), ForeignKey('base_articles.entry_id'), nullable=False)
    category = Column(Integer, nullable=False)


class BaseList(BaseBase):
    __tablename__ = 'cat_base'

    id = Column(Integer, primary_key=True, autoincrement=True)
    base_category = Column(String(100), nullable=False)

    children_base = relationship('CatList')


class GeneralCatList(BaseBase):
    __tablename__ = 'cat_list_general'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)


class CatList(BaseBase):
    __tablename__ = 'cat_list'

    id = Column(Integer, primary_key=True, autoincrement=True)
    base_id = Column(Integer, ForeignKey('cat_base.id'), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)

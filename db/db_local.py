#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import os

# Internal
from addons.config import ConfigDBLocal, ConfigProject

from _db_connection import ConnectDB

from db_base import Base

# External
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class LocalConnectDB(ConnectDB):
    def __init__(self, config_path=None):
        Session = self.start_db(config_path)
        self.session = Session()

    def start_db(self, config_path):
        project_config = ConfigProject(config_path)
        db_config = ConfigDBLocal(config_path)
        path = os.path.join(project_config.project_path,
                            db_config.path,
                            'local.db')

        engine = create_engine(f'sqlite:///{path}')
        Base.metadata.create_all(engine, checkfirst=True)
        session = sessionmaker(bind=engine)

        return session


if __name__ == '__main__':
    config_path = r'E:\Projects\NeuralDiploma\conf\project.cfg'
    con = LocalConnectDB(config_path)

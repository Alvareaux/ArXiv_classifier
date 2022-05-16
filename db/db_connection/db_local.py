#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import os

# Internal
from addons.config import ConfigDBLocal, ConfigProject
from db.db_connection._db_connection import ConnectDB

# External
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class LocalConnectDB(ConnectDB):
    def __init__(self, base, base_name, config_path=None):
        super().__init__(base, base_name, config_path)

    def start_db(self, config_path):
        project_config = ConfigProject(config_path)
        db_config = ConfigDBLocal(config_path)
        path = os.path.join(project_config.project_path,
                            db_config.path,
                            self.base_name)

        engine = create_engine(f'sqlite:///{path}')
        self.base.metadata.create_all(engine, checkfirst=True)
        session = sessionmaker(bind=engine)

        return session


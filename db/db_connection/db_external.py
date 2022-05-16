#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal
from addons.config import ConfigDBExternal
from db.db_connection._db_connection import ConnectDB

# External
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class ExternalConnectDB(ConnectDB):
    def __init__(self, base, base_name, config_path=None):
        super().__init__(base, config_path)

    def start_db(self, config_path):
        db_config = ConfigDBExternal(config_path)

        user = db_config.user
        password = db_config.password
        hostname = db_config.hostname
        dbname = db_config.dbname
        charset = db_config.charset

        engine = create_engine(f'mysql+pymysql://{user}:{password}@{hostname}/{dbname}?charset={charset}')
        self.base.metadata.create_all(engine, checkfirst=True)
        session = sessionmaker(bind=engine)

        return session

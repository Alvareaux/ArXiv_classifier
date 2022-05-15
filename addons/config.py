#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import os
import configparser

# Internal

# External


def inside_docker():
    docker_key = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)

    return docker_key


def get_path():
    if inside_docker():
        return '\\conf\\'
    else:
        return '..\\conf\\'


class ConfigProject:
    def __init__(self, path=None):
        self.config = configparser.ConfigParser()

        if not path:
            path = get_path()

        self.config.read(path)

        self.project_path, \
        self.db_type \
            = self.init_config_base()

    def init_config_base(self):
        if not inside_docker():
            project_path = self.config['PROJECT']['project_path_local']
        else:
            project_path = '\\'

        db_type = self.config['PROJECT']['db_type']

        return project_path, db_type


class ConfigDBLocal:
    def __init__(self, path=None):
        self.config = configparser.ConfigParser()

        if not path:
            path = get_path()

        self.config.read(path)

        self.path, \
        self.local_db \
            = self.init_config_base()

    def init_config_base(self):
        path = self.config['LOCAL']['path']
        local_db = self.config['LOCAL']['local_db']

        return path, local_db


class ConfigDBExternal:
    def __init__(self, path=None):
        self.config = configparser.ConfigParser()

        if not path:
            path = get_path()

        self.config.read(path)

        self.hostname, \
        self.port, \
        self.dbname, \
        self.user, \
        self.password, \
        self.charset, \
            = self.init_config_base()

    def init_config_base(self):
        hostname = self.config['EXTERNAL']['hostname']
        port = self.config['EXTERNAL']['port']
        dbname = self.config['EXTERNAL']['dbname']
        user = self.config['EXTERNAL']['user']
        password = self.config['EXTERNAL']['password']
        charset = self.config['EXTERNAL']['charset']

        return hostname, port, dbname, user, password, charset

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


class Config:
    def __init__(self, path=None):
        self.config = configparser.ConfigParser()

        if not path:
            path = get_path()

        self.config.read(path)


class ConfigProject(Config):
    def __init__(self, path=None):
        super().__init__(path)

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


class ConfigDBLocal(Config):
    def __init__(self, path=None):
        super().__init__(path)

        self.path, \
        self.local_db \
            = self.init_config_base()

    def init_config_base(self):
        path = self.config['LOCAL']['path']
        local_db = self.config['LOCAL']['local_db']

        return path, local_db


class ConfigDBExternal(Config):
    def __init__(self, path=None):
        super().__init__(path)

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


class ConfigArxiv(Config):
    def __init__(self, path=None):
        super().__init__(path)

        self.bath_size, \
        self.delay_seconds, \
        self.num_retries, \
            = self.init_config_base()

    def init_config_base(self):
        bath_size = int(self.config['ARXIV_API']['bath_size'])
        delay_seconds = int(self.config['ARXIV_API']['delay_seconds'])
        num_retries = int(self.config['ARXIV_API']['num_retries'])

        return bath_size, delay_seconds, num_retries


class ConfigUnit:
    def __init__(self, config_path_unit):
        self.config = configparser.ConfigParser()
        self.config.read(config_path_unit)

        self.base_model_path = self.init_config_data()

        self.threshold = self.init_config_neural()

    # -----------------------------------------------------------------------------------------------------------------

    def init_config_data(self):
        base_model_path = self.config['DATA']['BaseModelPath']

        return base_model_path

    def init_config_neural(self):
        threshold = float(self.config['UNIT']['Threshold'])

        return threshold


class ConfigMaster:
    def __init__(self, config_path_master):
        self.config = configparser.ConfigParser()
        self.config.read(config_path_master)

        self.instance_count, \
        self.clock, \
        self.unit, \
        self.update_time, \
            = self.init_config_process()

        self.timeout \
            = self.init_config_timings()

        self.server, \
        self.username, \
        self.password, \
        self.heartbeat, \
        self.n_queue_process_queue, \
        self.n_queue_process_queue_bulk, \
        self.n_queue_response_queue, \
        self.n_queue_response_queue_bulk, \
        self.n_queue_master_manage, \
        self.n_queue_master_monitor, \
        self.n_queue_master_monitor_queue, \
        self.n_queue_logger_base \
            = self.init_config_server()

    # -----------------------------------------------------------------------------------------------------------------

    def init_config_process(self):
        instance_count = int(self.config['MASTER']['InstanceCount'])

        clock = self.config['MODULES']['Clock']
        unit = self.config['MODULES']['Unit']

        timeout = int(self.config['CLOCK']['Timeout'])

        return instance_count, clock, unit, timeout

    def init_config_server(self):
        server = self.config['SERVER']['Server']
        username = self.config['SERVER']['Username']
        password = self.config['SERVER']['Password']

        heartbeat = self.config['SERVER']['Heartbeat']

        n_queue_process_queue = self.config['QUEUE']['ProcessQueue']
        n_queue_process_queue_bulk = self.config['QUEUE']['ProcessQueueBulk']
        n_queue_response_queue = self.config['QUEUE']['ResponseQueue']
        n_queue_response_queue_bulk = self.config['QUEUE']['ResponseQueueBulk']
        n_queue_master_manage = self.config['QUEUE']['MasterManage']
        n_queue_master_monitor = self.config['QUEUE']['MasterMonitor']
        n_queue_master_monitor_queue = self.config['QUEUE']['MasterMonitorQueue']
        n_queue_logger_base = self.config['QUEUE']['LoggerBase']

        return server, username, password, heartbeat, \
               n_queue_process_queue, n_queue_process_queue_bulk, n_queue_response_queue, n_queue_response_queue_bulk, \
               n_queue_master_manage, n_queue_master_monitor, n_queue_master_monitor_queue, n_queue_logger_base

    def init_config_timings(self):
        timeout = int(self.config['CLOCK']['Timeout'])

        return timeout

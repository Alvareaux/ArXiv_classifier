#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import sys
import time
import json

# Internal
from addons.config import ConfigMaster

# External
import pika

# ---------------------------------------------------------------------------------------------------------------------


class Clock:
    logger_prefix = '[C]'

    def __init__(self, config_path_master):
        self.config = ConfigMaster(config_path_master)

        self.channel, \
        self.queue_clock \
            = self.init_pika()

    def init_pika(self):
        parameters = pika.URLParameters(f'amqp://{self.config.username}:{self.config.password}'
                                        f'@{self.config.server}/?heartbeat={self.config.heartbeat}')
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)

        queue_clock = channel.queue_declare(
            self.config.n_queue_master_manage,
            durable=True
        )

        return channel, queue_clock

    def start(self):
        while True:
            self.update()
            print(f'{self.logger_prefix} Update request send with timeout {self.config.timeout}')
            time.sleep(self.config.timeout)

    def update(self):
        message = {'type': 'update_request',
                   }

        json_message = json.dumps(message)

        self.channel.basic_publish(exchange='', body=json_message.encode(encoding='UTF-8'),
                                   routing_key=self.config.n_queue_master_manage)

    def clear_queue(self, queue):
        self.channel.queue_purge(queue)


if __name__ == "__main__":
    if sys.platform == "linux" or sys.platform == "linux2":
        config_path_project = 'conf/project.cfg'
        config_path_master = 'conf/server.cfg'
    else:
        config_path_project = '../conf/project.cfg'
        config_path_master = '../conf/server.cfg'

    clock = Clock(config_path_master)
    clock.start()

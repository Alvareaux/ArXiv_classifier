#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import json
import sys
import subprocess
import time

# Internal
import multiprocessing
from addons.config import ConfigMaster

# External
from PyQt6.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsPixmapItem, QFileDialog
from PyQt6.QtCore import Qt, QLineF, pyqtSignal, QThread, pyqtSignal, QObject, QRunnable
from PyQt6.QtGui import QPixmap, QPen

import pika


class Signals(QObject):
    type_signal = pyqtSignal(int)
    result_signal = pyqtSignal(tuple)


class QueueUpdater(QRunnable):
    signals = Signals()

    plot_type = 1

    plot_lim = 50
    plot_data_global_size = [0] * (plot_lim + 1)
    plot_data_local_size = [0] * (plot_lim + 1)
    plot_data_master_manage_size = [0] * (plot_lim + 1)

    def __init__(self, config):
        super(QueueUpdater, self).__init__()

        self.config = config

        self.channel, \
        self.connection, \
        self.queue_master_monitor_queue, \
            = self.init_pika()

    def on_message(self, ch, method, properties, body):
        json_msg = json.loads(body, strict=False)
        type = json_msg['type']

        if type == 'queue_statuses':
            q_global_size = json_msg['q_global_size']
            q_local_size = json_msg['q_local_size']
            q_master_manage_size = json_msg['q_master_manage_size']

            self.plot_data_global_size = self.append_and_check(self.plot_data_global_size,
                                                               q_global_size)
            self.plot_data_local_size = self.append_and_check(self.plot_data_local_size,
                                                              q_local_size)
            self.plot_data_master_manage_size = self.append_and_check(self.plot_data_master_manage_size,
                                                                      q_master_manage_size)

            self.plot()

        self.channel.basic_ack(method.delivery_tag)
        return

    def append_and_check(self, queue, size):
        queue.append(size)

        if len(queue) > self.plot_lim + 1:
            queue = queue[-(self.plot_lim + 1):]

        return queue

    def plot(self):
        x = list(range(-self.plot_lim, 1))

        if self.plot_type == 1:
            y = self.plot_data_global_size
        elif self.plot_type == 2:
            y = self.plot_data_local_size
        elif self.plot_type == 3:
            y = self.plot_data_master_manage_size
        else:
            raise Exception(f'Invalid plot type: {self.plot_type}')

        self.signals.result_signal.emit((x, y))

    def set_plot_type(self, plot_type):
        self.plot_type = plot_type

    def init_pika(self):
        parameters = pika.URLParameters(f'amqp://{self.config.username}:{self.config.password}'
                                        f'@{self.config.server}/?heartbeat={self.config.heartbeat}')
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)

        queue_master_monitor_queue = channel.queue_declare(
            self.config.n_queue_master_monitor_queue,
            durable=True
        )

        return channel, connection, queue_master_monitor_queue

    def prepare(self):
        self.clear_queue(self.config.n_queue_master_monitor_queue)

    def run(self):
        self.prepare()

        self.channel.basic_consume(
            queue=self.config.n_queue_master_monitor_queue, on_message_callback=self.on_message)

        self.clear_queue(self.config.n_queue_master_monitor_queue)

        try:
            self.channel.start_consuming()
        except Exception as e:
            print(e)

        self.connection.close()

    def clear_queue(self, queue):
        self.channel.queue_purge(queue)

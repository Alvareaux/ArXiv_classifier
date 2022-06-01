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
    absolute_signal = pyqtSignal(bool)
    count_signal = pyqtSignal(int)

    cpu_signal_1 = pyqtSignal(int)
    cpu_signal_2 = pyqtSignal(int)
    cpu_signal_3 = pyqtSignal(int)
    cpu_signal_4 = pyqtSignal(int)
    cpu_signal_5 = pyqtSignal(int)
    cpu_signal_6 = pyqtSignal(int)
    cpu_signal_7 = pyqtSignal(int)

    mem_signal_1 = pyqtSignal(int)
    mem_signal_2 = pyqtSignal(int)
    mem_signal_3 = pyqtSignal(int)
    mem_signal_4 = pyqtSignal(int)
    mem_signal_5 = pyqtSignal(int)
    mem_signal_6 = pyqtSignal(int)
    mem_signal_7 = pyqtSignal(int)

    frz_signal_1 = pyqtSignal(bool)
    frz_signal_2 = pyqtSignal(bool)
    frz_signal_3 = pyqtSignal(bool)
    frz_signal_4 = pyqtSignal(bool)
    frz_signal_5 = pyqtSignal(bool)
    frz_signal_6 = pyqtSignal(bool)
    frz_signal_7 = pyqtSignal(bool)

    que_signal_1 = pyqtSignal(str)
    que_signal_2 = pyqtSignal(str)
    que_signal_3 = pyqtSignal(str)
    que_signal_4 = pyqtSignal(str)
    que_signal_5 = pyqtSignal(str)
    que_signal_6 = pyqtSignal(str)
    que_signal_7 = pyqtSignal(str)


class ResourceUpdater(QRunnable):
    absolute = False
    count = 5

    cpu_signals = []
    mem_signals = []
    que_signals = []

    signals = Signals()

    def __init__(self, config):
        super(ResourceUpdater, self).__init__()

        self.config = config

        self.channel, \
        self.connection, \
        self.queue_master_monitor, \
            = self.init_pika()

        self.setup_signals()

    def on_message(self, ch, method, properties, body):
        json_msg = json.loads(body, strict=False)
        type = json_msg['type']

        if type == 'progress_bar_update':
            p_id = json_msg['id']
            if 0 <= p_id <= 6:
                process_cpu = json_msg['process_cpu']
                process_mem = json_msg['process_mem']

                freeze_status = json_msg['frozen']
                queue_status = json_msg['queue']

                if self.absolute:
                    cpu_value = int(process_cpu / multiprocessing.cpu_count())
                    mem_value = int(process_mem)
                else:
                    cpu_value = int(process_cpu / multiprocessing.cpu_count() * self.count)
                    mem_value = int(process_mem * self.count)

                self.cpu_signals[p_id].emit(cpu_value)
                self.mem_signals[p_id].emit(mem_value)
                self.frz_signals[p_id].emit(freeze_status)
                self.que_signals[p_id].emit(queue_status)
            else:
                raise Exception(f'Value of unit_count out of boundaries: {json_msg["p_id"]}')

        self.channel.basic_ack(method.delivery_tag)
        return

    def setup_signals(self):
        self.cpu_signals = [self.signals.cpu_signal_1, self.signals.cpu_signal_2, self.signals.cpu_signal_3,
                            self.signals.cpu_signal_4, self.signals.cpu_signal_5, self.signals.cpu_signal_6,
                            self.signals.cpu_signal_7]
        self.mem_signals = [self.signals.mem_signal_1, self.signals.mem_signal_2, self.signals.mem_signal_3,
                            self.signals.mem_signal_4, self.signals.mem_signal_5, self.signals.mem_signal_6,
                            self.signals.mem_signal_7]
        self.frz_signals = [self.signals.frz_signal_1, self.signals.frz_signal_2, self.signals.frz_signal_3,
                            self.signals.frz_signal_4, self.signals.frz_signal_5, self.signals.frz_signal_6,
                            self.signals.frz_signal_7]
        self.que_signals = [self.signals.que_signal_1, self.signals.que_signal_2, self.signals.que_signal_3,
                            self.signals.que_signal_4, self.signals.que_signal_5, self.signals.que_signal_6,
                            self.signals.que_signal_7]

    def set_absolute(self, absolute):
        self.absolute = absolute

    def set_count(self, count):
        self.count = count

    def init_pika(self):
        parameters = pika.URLParameters(f'amqp://{self.config.username}:{self.config.password}'
                                        f'@{self.config.server}/?heartbeat={self.config.heartbeat}')
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)

        queue_master_monitor = channel.queue_declare(
            self.config.n_queue_master_monitor,
            durable=True
        )

        return channel, connection, queue_master_monitor

    def prepare(self):
        self.clear_queue(self.config.n_queue_master_monitor)

    def run(self):
        self.prepare()

        self.channel.basic_consume(
            queue=self.config.n_queue_master_monitor, on_message_callback=self.on_message)

        self.clear_queue(self.config.n_queue_master_monitor)

        try:
            self.channel.start_consuming()
        except Exception as e:
            print(e)

        self.connection.close()

    def clear_queue(self, queue):
        self.channel.queue_purge(queue)

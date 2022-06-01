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
    log_signal = pyqtSignal(str)


class LogUpdater(QRunnable):
    signals = Signals()

    log_lim = 13
    log_text = []

    def __init__(self, config):
        super(LogUpdater, self).__init__()

        self.config = config

        self.channel, \
        self.connection, \
        self.queue_logger_base \
            = self.init_pika()

    def on_message(self, ch, method, properties, body):
        self.log_text.append(str(body)[2:-1])

        if len(self.log_text) > self.log_lim:
            self.log_text = self.log_text[-self.log_lim:]

        self.signals.log_signal.emit('\n'.join(self.log_text))

        self.channel.basic_ack(method.delivery_tag)
        return

    def init_pika(self):
        parameters = pika.URLParameters(f'amqp://{self.config.username}:{self.config.password}'
                                        f'@{self.config.server}/?heartbeat={self.config.heartbeat}')
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)

        queue_logger_base = channel.queue_declare(
            self.config.n_queue_logger_base,
            durable=True
        )

        return channel, connection, queue_logger_base

    def prepare(self):
        self.clear_queue(self.config.n_queue_logger_base)

    def run(self):
        self.prepare()

        self.channel.basic_consume(
            queue=self.config.n_queue_logger_base, on_message_callback=self.on_message)

        self.clear_queue(self.config.n_queue_logger_base)

        try:
            self.channel.start_consuming()
        except Exception as e:
            print(e)

        self.connection.close()

    def clear_queue(self, queue):
        self.channel.queue_purge(queue)

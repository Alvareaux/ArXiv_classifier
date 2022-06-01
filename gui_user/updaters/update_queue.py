#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import ast
import json
import sys
import subprocess
import time

# Internal
import multiprocessing
from addons.config import ConfigMaster

# External
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QDialog, \
    QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QLineF, pyqtSignal, QThread, pyqtSignal, QObject, QRunnable, QEventLoop
from PyQt5.QtGui import QPixmap, QPen

import pika


class Signals(QObject):
    dialog_signal = pyqtSignal(str)
    pause_signal = pyqtSignal(bool)


class QueueUpdater(QRunnable):
    signals = Signals()

    pause = True

    def __init__(self, config, labels_dict):
        super(QueueUpdater, self).__init__()

        self.config = config

        self.labels_dict = labels_dict

        self.channel, \
        self.connection, \
        self.queue_response_queue, \
            = self.init_pika()

    def on_message(self, ch, method, properties, body):
        json_msg = json.loads(body, strict=False)

        entry_id = json_msg['entry_id']
        labels = ast.literal_eval(json_msg['labels'])

        if not json_msg['null']:
            labels_text = []
            for label in labels.keys():
                prob = labels[label]

                labels_text.append(f'{(prob * 100):.2f}% - {self.labels_dict[label] }')

            if labels_text:
                text = f'Entry ID: {entry_id}\n\n' \
                       f'Labels:\n' + '\n'.join(labels_text)
            else:
                text = f'Entry ID: {entry_id}\n\n' \
                       f'Labels: None'

            self.signals.dialog_signal.emit(text)

            while self.pause:
                time.sleep(1)
            self.pause = True

        self.channel.basic_ack(method.delivery_tag)
        return

    def init_pika(self):
        parameters = pika.URLParameters(f'amqp://{self.config.username}:{self.config.password}'
                                        f'@{self.config.server}/?heartbeat={self.config.heartbeat}')
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)

        queue_response_queue = channel.queue_declare(
            self.config.n_queue_response_queue,
            durable=True
        )

        return channel, connection, queue_response_queue

    def prepare(self):
        self.clear_queue(self.config.n_queue_master_monitor_queue)

    def run(self):
        self.prepare()

        self.channel.basic_consume(
            queue=self.config.n_queue_response_queue, on_message_callback=self.on_message)

        self.clear_queue(self.config.n_queue_response_queue)

        try:
            self.channel.start_consuming()
        except Exception as e:
            print(e)

        self.connection.close()

    def set_pause(self, pause):
        self.pause = pause

    def clear_queue(self, queue):
        self.channel.queue_purge(queue)

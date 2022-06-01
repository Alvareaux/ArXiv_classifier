#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import gc
import sys
import json

# Internal
from db.db_init.db_init_base import BaseBase, base_name
from db.db_connection.db_external import ExternalConnectDB

from addons.timer import Timer
from addons.config import ConfigMaster, ConfigUnit

from models.keras_model_base import KerasModel
from pipeline.clear_text import TextCleaner
from pipeline.preprocess_text import TextPreprocessor

from messengers.messenger_unit import Sender

# External
import pika

if sys.platform == "linux" or sys.platform == "linux2":
    config_path_project = 'conf/project.cfg'
    config_path_master = 'conf/server.cfg'
else:
    config_path_project = '../conf/project.cfg'
    config_path_master = '../conf/server.cfg'


class NeuralUnit:
    logger_prefix = '[U]'

    response_queue = None

    def __init__(self):
        self.num = sys.argv[1]

        if '-queue' in sys.argv[2:]:
            self.type = 'queue'
        elif '-validate' in sys.argv[2:]:
            self.type = 'validate'
        else:
            self.type = 'personal'

        self.config = ConfigMaster(config_path_master)
        self.config_unit = ConfigUnit(config_path_master)

        self.connection, self.channel = self.init_pika()

        self.sender = Sender(self.channel, self.config)

        self.text_cleaner = TextCleaner()
        self.text_preprocessor = TextPreprocessor()

        self.models = {
            'base': KerasModel(self.config_unit.base_model_path),
        }

        self.main()

    def main(self):
        if self.type == 'queue' or self.type == 'validate':
            self.channel.basic_consume(
                queue=self.config.n_queue_process_queue_bulk, on_message_callback=self.on_message)

            self.response_queue = self.config.n_queue_response_queue_bulk
        elif self.type == 'personal':
            self.channel.basic_consume(
                queue=self.config.n_queue_process_queue, on_message_callback=self.on_message)

            self.response_queue = self.config.n_queue_response_queue
        else:
            raise Exception('Wrong process type')

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()

        self.connection.close()

    def pipeline(self, body):
        json_msg = json.loads(body, strict=False)

        text_id, text = json_msg['entry_id'], json_msg['text']

        timer = Timer()
        timer.start()

        text = self.text_cleaner.text_clearing_pipeline(text, lowercase=True)
        text = self.text_preprocessor.lemmatize(text)

        text_enc = text.encode('utf-8')

        labels = self.models['base'].score_text(text_enc)

        new_labels = {}
        for k, v in labels.items():
            if v >= self.config_unit.threshold:
                new_labels[k] = v
        labels = new_labels

        self.log(f'Text {text_id} successfully analyzed in {timer.finish()}')

        if self.type == 'personal':
            self.sender.respond(entry_id=text_id, labels=labels, null=json_msg['null'], queue=self.response_queue)
        elif self.type == 'queue':
            self.sender.respond_queue(entry_id=text_id, labels=labels, queue=self.response_queue)
        elif self.type == 'validate':
            self.sender.respond_validate(entry_id=text_id, labels=list(labels.keys()), original_labels=json_msg['original_labels'],
                                         queue=self.response_queue)

    def on_message(self, ch, method, properties, body):
        self.pipeline(body)

        self.channel.basic_ack(method.delivery_tag)
        gc.collect()

        return

    def init_pika(self):
        parameters = pika.URLParameters(f'amqp://{self.config.username}:{self.config.password}@{self.config.server}'
                                        f'/?heartbeat=5')
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)

        queue_process_queue = channel.queue_declare(
            self.config.n_queue_process_queue,
            durable=True
        )

        queue_process_queue_bulk = channel.queue_declare(
            self.config.n_queue_process_queue_bulk,
            durable=True
        )

        queue_response_queue = channel.queue_declare(
            self.config.n_queue_response_queue,
            durable=True
        )

        queue_response_queue_bulk = channel.queue_declare(
            self.config.n_queue_response_queue_bulk,
            durable=True
        )

        queue_logger_base = channel.queue_declare(
            self.config.n_queue_logger_base,
            durable=True
        )

        return connection, channel

    def log(self, msg):
        msg = self.logger_prefix + f' Unit {int(self.num) + 1}: ' + msg
        print(msg)
        self.sender.send_log(msg)


if __name__ == '__main__':
    print('[*] Base unit started. Waiting for messages. To exit press CTRL+C')
    unit = NeuralUnit()

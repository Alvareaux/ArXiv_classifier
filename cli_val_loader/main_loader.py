#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import json

# Internal
from addons.config import ConfigMaster

from db.db_init.db_init_base import BaseBase, base_name, ValCategories
from db.db_connection.db_external import ExternalConnectDB

# External
import pika


class Loader:
    def __init__(self, db, config_path):
        self.db = db
        self.config = ConfigMaster(config_path)

        self.channel, \
        self.connection, \
        self.queue_response_queue_bulk, \
            = self.init_pika()

    def on_message(self, ch, method, properties, body):
        json_msg = json.loads(body, strict=False)

        entry_id = json_msg['entry_id']
        labels = json_msg['labels']
        original_labels = json_msg['original_labels']

        new_val_cats = ValCategories(entry_id=entry_id,
                                     category_base=original_labels,
                                     category_pred=labels)

        self.db.session.add(new_val_cats)
        self.db.session.commit()

        self.channel.basic_ack(method.delivery_tag)
        return

    def run(self):
        self.channel.basic_consume(
            queue=self.config.n_queue_response_queue_bulk, on_message_callback=self.on_message)

        try:
            self.channel.start_consuming()
        except Exception as e:
            print(e)

        self.connection.close()

    def init_pika(self):
        parameters = pika.URLParameters(f'amqp://{self.config.username}:{self.config.password}'
                                        f'@{self.config.server}/?heartbeat={self.config.heartbeat}')
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)

        queue_response_queue_bulk = channel.queue_declare(
            self.config.n_queue_response_queue_bulk,
            durable=True
        )

        return channel, connection, queue_response_queue_bulk


if __name__ == '__main__':
    config_path = r'E:\Projects\NeuralDiploma\conf\project.cfg'
    config_path_server = r'E:\Projects\NeuralDiploma\conf\server.cfg'

    db_ext = ExternalConnectDB(BaseBase, base_name, config_path)

    val = Loader(db_ext, config_path_server)
    val.run()

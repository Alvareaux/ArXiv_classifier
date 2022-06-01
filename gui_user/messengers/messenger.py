#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import json

# Internal

# External


class Sender:
    def __init__(self, channel, config):
        self.channel = channel
        self.config = config

    def send_result(self, queue, message):
        self.channel.basic_publish(exchange='', body=message.encode(encoding='UTF-8'),
                                   routing_key=queue)

    def send_text_app(self, entry_id, text):
        message = {'entry_id': entry_id,
                   'text': text,
                   'null': False
                   }

        json_message = json.dumps(message)
        self.send_result(self.config.n_queue_process_queue, json_message)

    def send_text_db(self, entry_id, text):
        message = {'entry_id': entry_id,
                   'text': text,
                   }

        json_message = json.dumps(message)
        self.send_result(self.config.n_queue_process_queue, json_message)

    def send_text_null(self, entry_id, text):
        message = {'entry_id': entry_id,
                   'text': text,
                   'null': True
                   }

        json_message = json.dumps(message)
        self.send_result(self.config.n_queue_process_queue, json_message)
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

    def respond(self, entry_id, labels, null, queue):
        message = {'entry_id': entry_id,
                   'labels': str(labels),
                   'null': null
                   }

        json_message = json.dumps(message)
        self.send_result(queue, json_message)

    def respond_queue(self, entry_id, labels, queue):
        message = {'entry_id': entry_id,
                   'labels': str(labels),
                   }

        json_message = json.dumps(message)
        self.send_result(queue, json_message)

    def respond_validate(self, entry_id, labels, original_labels, queue):
        message = {'entry_id': entry_id,
                   'labels': str(labels),
                   'original_labels': str(original_labels)
                   }

        json_message = json.dumps(message)
        self.send_result(queue, json_message)

    def send_log(self, msg):
        self.send_result(self.config.n_queue_logger_base, msg)

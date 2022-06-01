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

    def freeze_process(self, process_id):
        message = {'type': 'freeze_process_request',
                   'id': process_id,
                   }

        json_message = json.dumps(message)
        self.send_result(self.config.n_queue_master_manage, json_message)

    def unfreeze_process(self, process_id):
        message = {'type': 'unfreeze_process_request',
                   'id': process_id,
                   }

        json_message = json.dumps(message)
        self.send_result(self.config.n_queue_master_manage, json_message)

    def reload_process(self, process_id):
        message = {'type': 'reload_process_request',
                   'id': process_id,
                   }

        json_message = json.dumps(message)
        self.send_result(self.config.n_queue_master_manage, json_message)

    def add_unit(self):
        message = {'type': 'add_unit_request',
                   }

        json_message = json.dumps(message)
        self.send_result(self.config.n_queue_master_manage, json_message)

    def remove_unit(self):
        message = {'type': 'remove_unit_request',
                   }

        json_message = json.dumps(message)
        self.send_result(self.config.n_queue_master_manage, json_message)

    def change_queue_status_unit(self, process_id, queue):
        message = {'type': 'change_bulk_status_request',
                   'id': process_id,
                   'queue': queue
                   }

        json_message = json.dumps(message)
        self.send_result(self.config.n_queue_master_manage, json_message)
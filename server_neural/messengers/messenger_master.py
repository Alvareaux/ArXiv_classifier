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

    def update_processes_push(self, process_id, process_mem, process_cpu, frozen, queue):
        message = {'type': 'progress_bar_update',
                   'id': process_id,
                   'process_mem': process_mem,
                   'process_cpu': process_cpu,
                   'frozen': frozen,
                   'queue': queue
                   }

        json_message = json.dumps(message)
        self.send_result(self.config.n_queue_master_monitor, json_message)

    def queue_statuses_push(self, q_global_size, q_local_size, q_master_manage_size):
        message = {'type': 'queue_statuses',
                   'q_global_size': q_global_size,
                   'q_local_size': q_local_size,
                   'q_master_manage_size': q_master_manage_size,
                   }

        json_message = json.dumps(message)
        self.send_result(self.config.n_queue_master_monitor_queue, json_message)

    def send_log(self, msg):
        self.send_result(self.config.n_queue_logger_base, msg)

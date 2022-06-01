#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import json
import sys
import subprocess
import time

# Internal
from addons.config import ConfigMaster
from messengers.messenger_master import Sender

# External
import nltk
import psutil
import pika


class NeuralMaster:
    logger_prefix = '[M]'

    sleep_time = 20

    procs = []
    nltk.download("stopwords")

    clock_proc = None

    freeze_status = [False] * 7
    queue_status = ['A'] * 7

    def __init__(self, config_path_master):
        self.config = ConfigMaster(config_path_master)

        self.channel, \
        self.connection, \
        self.queue_master_manage, \
        self.queue_master_monitor, \
        self.queue_logger_base \
            = self.init_pika()

        self.sender = Sender(self.channel, self.config)

        self.clock_proc = self.process_clock()

        self.prepare()
        self.run()

    def init_pika(self):
        parameters = pika.URLParameters(f'amqp://{self.config.username}:{self.config.password}'
                                        f'@{self.config.server}/?heartbeat={self.config.heartbeat}')
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

        queue_master_manage = channel.queue_declare(
            self.config.n_queue_master_manage,
            durable=True
        )

        queue_master_monitor = channel.queue_declare(
            self.config.n_queue_master_monitor,
            durable=True
        )

        queue_master_monitor = channel.queue_declare(
            self.config.n_queue_master_monitor_queue,
            durable=True
        )

        queue_logger_base = channel.queue_declare(
            self.config.n_queue_logger_base,
            durable=True
        )

        return channel, connection, queue_master_manage, queue_master_monitor, queue_logger_base

    def prepare(self):
        self.clear_queue(self.config.n_queue_logger_base)
        self.clear_queue(self.config.n_queue_master_manage)
        self.process_unit()

    def run(self):
        self.channel.basic_consume(
            queue=self.config.n_queue_master_manage, on_message_callback=self.on_message)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()

        self.connection.close()

    def on_message(self, ch, method, properties, body):
        json_msg = json.loads(body, strict=False)
        type = json_msg['type']

        if type == 'update_request':
            self.update_processes(self.procs)
            self.send_queue_statuses()
        elif type == 'freeze_process_request':
            self.freeze_process(json_msg['id'])
        elif type == 'unfreeze_process_request':
            self.freeze_process(json_msg['id'], unfreeze=True)
        elif type == 'reload_process_request':
            self.reload_process(json_msg['id'])
        elif type == 'change_bulk_status_request':
            self.change_queue(json_msg['id'], json_msg['queue'])
        elif type == 'add_unit_request':
            self.add_unit()
        elif type == 'remove_unit_request':
            self.remove_unit()

        self.channel.basic_ack(method.delivery_tag)
        return

    def change_queue(self, num, queue):
        proc = self.procs[num]
        proc.kill()

        self.queue_status[num] = queue

        self.reload_process(num)

    def add_unit(self):
        if len(self.procs) < 7:
            proc = subprocess.Popen([sys.executable, self.config.unit, str(len(self.procs))])
            self.procs.append(proc)

    def remove_unit(self):
        proc = self.procs[-1]
        self.procs.remove(proc)
        proc.kill()

    def update_processes(self, procs):
        for p in enumerate(procs):
            process_id = p[0]
            process = p[1]

            mem_usage = self.full_mem_usage(process)
            cpu_usage = self.full_cpu_usage(process)

            self.sender.update_processes_push(process_id,
                                              mem_usage,
                                              cpu_usage,
                                              self.freeze_status[process_id],
                                              self.queue_status[process_id])

    def send_queue_statuses(self):
        q_global_size = self.get_queue_size(self.config.n_queue_process_queue_bulk)
        q_local_size = self.get_queue_size(self.config.n_queue_process_queue)
        q_master_manage_size = self.get_queue_size(self.config.n_queue_master_manage)

        self.sender.queue_statuses_push(q_global_size, q_local_size, q_master_manage_size)

    def freeze_process(self, num, unfreeze=False):
        process = psutil.Process(self.procs[num].pid)
        children = process.children(recursive=True)

        if not unfreeze:
            process.suspend()
            self.freeze_status[num] = True
            for child in children:
                child.suspend()
            self.log(f'Process {num + 1} freezed')
        else:
            process.resume()
            self.freeze_status[num] = False
            for child in children:
                child.resume()
            self.log(f'Process {num + 1} resumed')

    def reload_process(self, num):
        process = self.procs[num]
        process.kill()

        if self.queue_status[num] == 'A':
            proc = subprocess.Popen([sys.executable, self.config.unit, str(num)])
        elif self.queue_status[num] == 'B':
            proc = subprocess.Popen([sys.executable, self.config.unit, str(num), '-queue'])
        elif self.queue_status[num] == 'C':
            proc = subprocess.Popen([sys.executable, self.config.unit, str(num), '-validate'])
        else:
            proc = subprocess.Popen([sys.executable, self.config.unit, str(num)])

        self.procs[num] = proc

        self.log(f'Process {num + 1} reloaded')

    def full_cpu_usage(self, parent):
        parent = psutil.Process(parent.pid)
        parent_cpu = psutil.Process(parent.pid).cpu_percent(interval=0.1)

        children_cpu = 0
        children = parent.children(recursive=True)
        for child in children:
            children_cpu += psutil.Process(child.pid).cpu_percent(interval=0.1)

        return parent_cpu + children_cpu

    def full_mem_usage(self, parent):
        parent = psutil.Process(parent.pid)
        parent_mem_prc = psutil.Process(parent.pid).memory_percent()

        children_mem_prc = 0
        children = parent.children(recursive=True)

        for child in children:
            children_mem_prc += psutil.Process(child.pid).memory_percent()

        return parent_mem_prc + children_mem_prc

    def process_clock(self):
        clock_proc = subprocess.Popen([sys.executable, self.config.clock], shell=False)

        return clock_proc

    def process_unit(self):
        for i in range(self.config.instance_count):
            proc = subprocess.Popen([sys.executable, self.config.unit, str(i)])
            self.procs.append(proc)
            time.sleep(self.sleep_time)

    def process_reload(self):
        for p in self.procs:
            self.procs.remove(p)
            p.kill()

        self.process_unit()

    def get_queue_size(self, queue) -> int:
        queue_task = self.channel.queue_declare(
            queue,
            durable=True,
            passive=True
        )

        return queue_task.method.message_count

    def clear_queue(self, queue):
        self.channel.queue_purge(queue)

    def log(self, msg):
        msg = self.logger_prefix + ' ' + msg
        print(msg)
        self.sender.send_log(msg)


if __name__ == "__main__":
    if sys.platform == "linux" or sys.platform == "linux2":
        config_path_project = 'conf/project.cfg'
        config_path_master = 'conf/server.cfg'
    else:
        config_path_project = '../conf/project.cfg'
        config_path_master = '../conf/server.cfg'

    master = NeuralMaster(config_path_master)

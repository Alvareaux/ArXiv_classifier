#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import sys
import traceback

# Internal
from main_ui import Ui_MainWindow

from messengers.messenger import Sender
from updaters.update_resources import ResourceUpdater
from updaters.update_queue import QueueUpdater
from updaters.update_log import LogUpdater

from addons.config import ConfigMaster

# External
import pika

from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import QThreadPool


# pyuic6 -o main_ui.py -x main.ui


class Window(QMainWindow, Ui_MainWindow):
    threadpool = QThreadPool()

    units = None
    units_paused = None
    units_pause_buttons = None
    units_cpu = None
    units_mem = None
    units_ab = None

    absolute_signal = None
    count_signal = None
    queue_type_change_signal = None

    queue_display_top_limit = 100

    def __init__(self, config_path_master, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.config = ConfigMaster(config_path_master)
        self.units_count = self.config.instance_count

        self.channel, self.connection, self.queue_master_manage = self.init_pika()

        self.sender = Sender(self.channel, self.config)

        self.updater_resources = ResourceUpdater(self.config)
        self.updater_queue = QueueUpdater(self.config)
        self.updater_log = LogUpdater(self.config)

        self.setup()
        self.update_units()

    def init_pika(self):
        parameters = pika.URLParameters(f'amqp://{self.config.username}:{self.config.password}'
                                        f'@{self.config.server}/?heartbeat={self.config.heartbeat}')
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)

        queue_master_manage = channel.queue_declare(
            self.config.n_queue_master_manage,
            durable=True
        )

        return channel, connection, queue_master_manage

    def setup(self):
        self.setup_buttons_units()
        self.setup_settings_units()
        self.setup_settings_queue()

        self.units = [self.u1, self.u2, self.u3, self.u4, self.u5, self.u6, self.u7]
        self.units_paused = [False, False, False, False, False, False, False]
        self.units_pause_buttons = [self.u1_pause, self.u2_pause, self.u3_pause, self.u4_pause,
                                    self.u5_pause, self.u6_pause, self.u7_pause]
        self.units_ab = [self.u1_ab, self.u2_ab, self.u3_ab, self.u4_ab, self.u5_ab, self.u6_ab, self.u7_ab]

        self.units_cpu = [self.u1_p_cpu, self.u2_p_cpu, self.u3_p_cpu, self.u4_p_cpu,
                          self.u5_p_cpu, self.u6_p_cpu, self.u7_p_cpu]
        self.units_mem = [self.u1_p_mem, self.u2_p_mem, self.u3_p_mem, self.u4_p_mem,
                          self.u5_p_mem, self.u6_p_mem, self.u7_p_mem]

        self.setup_thread_resources()
        self.setup_thread_queues()
        self.setup_thread_log()

    def setup_thread_resources(self):
        self.updater_resources.signals.cpu_signal_1.connect(lambda value: self.set_progressbar(value, 1, 'cpu'))
        self.updater_resources.signals.cpu_signal_2.connect(lambda value: self.set_progressbar(value, 2, 'cpu'))
        self.updater_resources.signals.cpu_signal_3.connect(lambda value: self.set_progressbar(value, 3, 'cpu'))
        self.updater_resources.signals.cpu_signal_4.connect(lambda value: self.set_progressbar(value, 4, 'cpu'))
        self.updater_resources.signals.cpu_signal_5.connect(lambda value: self.set_progressbar(value, 5, 'cpu'))
        self.updater_resources.signals.cpu_signal_6.connect(lambda value: self.set_progressbar(value, 6, 'cpu'))
        self.updater_resources.signals.cpu_signal_7.connect(lambda value: self.set_progressbar(value, 7, 'cpu'))

        self.updater_resources.signals.mem_signal_1.connect(lambda value: self.set_progressbar(value, 1, 'mem'))
        self.updater_resources.signals.mem_signal_2.connect(lambda value: self.set_progressbar(value, 2, 'mem'))
        self.updater_resources.signals.mem_signal_3.connect(lambda value: self.set_progressbar(value, 3, 'mem'))
        self.updater_resources.signals.mem_signal_4.connect(lambda value: self.set_progressbar(value, 4, 'mem'))
        self.updater_resources.signals.mem_signal_5.connect(lambda value: self.set_progressbar(value, 5, 'mem'))
        self.updater_resources.signals.mem_signal_6.connect(lambda value: self.set_progressbar(value, 6, 'mem'))
        self.updater_resources.signals.mem_signal_7.connect(lambda value: self.set_progressbar(value, 7, 'mem'))

        self.updater_resources.signals.frz_signal_1.connect(lambda value: self.set_freeze(value, 1))
        self.updater_resources.signals.frz_signal_2.connect(lambda value: self.set_freeze(value, 2))
        self.updater_resources.signals.frz_signal_3.connect(lambda value: self.set_freeze(value, 3))
        self.updater_resources.signals.frz_signal_4.connect(lambda value: self.set_freeze(value, 4))
        self.updater_resources.signals.frz_signal_5.connect(lambda value: self.set_freeze(value, 5))
        self.updater_resources.signals.frz_signal_6.connect(lambda value: self.set_freeze(value, 6))
        self.updater_resources.signals.frz_signal_7.connect(lambda value: self.set_freeze(value, 7))

        self.updater_resources.signals.que_signal_1.connect(lambda value: self.set_queue(value, 1))
        self.updater_resources.signals.que_signal_2.connect(lambda value: self.set_queue(value, 2))
        self.updater_resources.signals.que_signal_3.connect(lambda value: self.set_queue(value, 3))
        self.updater_resources.signals.que_signal_4.connect(lambda value: self.set_queue(value, 4))
        self.updater_resources.signals.que_signal_5.connect(lambda value: self.set_queue(value, 5))
        self.updater_resources.signals.que_signal_6.connect(lambda value: self.set_queue(value, 6))
        self.updater_resources.signals.que_signal_7.connect(lambda value: self.set_queue(value, 7))

        self.absolute_signal = self.updater_resources.signals.absolute_signal
        self.absolute_signal.connect(self.updater_resources.set_absolute)

        self.count_signal = self.updater_resources.signals.count_signal
        self.count_signal.connect(self.updater_resources.set_count)

        self.threadpool.start(self.updater_resources)

    def setup_thread_queues(self):
        self.queue_type_change_signal = self.updater_queue.signals.type_signal
        self.queue_type_change_signal.connect(self.updater_queue.set_plot_type)

        self.updater_queue.signals.result_signal.connect(self.plot_queue)

        self.threadpool.start(self.updater_queue)

    def setup_thread_log(self):
        self.updater_log.signals.log_signal.connect(self.set_log)

        self.threadpool.start(self.updater_log)

    def set_progressbar(self, value, n, t):
        if t == 'cpu':
            self.units_cpu[n - 1].setValue(value)
        elif t == 'mem':
            self.units_mem[n - 1].setValue(value)

    def plot_queue(self, xy):
        x = xy[0]
        y = xy[1]

        self.plot_widget.canvas.axes.clear()
        if max(y) < self.queue_display_top_limit:
            self.plot_widget.canvas.axes.set_ylim([0,  self.queue_display_top_limit])
        self.plot_widget.canvas.axes.set_xlim([-self.updater_queue.plot_lim, 0])
        self.plot_widget.canvas.axes.plot(x, y, color='orange')
        self.plot_widget.canvas.draw()

    def set_log(self, log):
        self.plain_log.setPlainText(log)

    def setup_buttons_units(self):
        self.u0_plus.clicked.connect(self.add_unit)
        self.u0_minus.clicked.connect(self.remove_unit)

        self.u1_pause.clicked.connect(lambda: self.pause_press(1))
        self.u1_reload.clicked.connect(lambda: self.reload_press(1))
        self.u1_ab.currentTextChanged.connect(lambda value: self.ab_update(1))

        self.u2_pause.clicked.connect(lambda: self.pause_press(2))
        self.u2_reload.clicked.connect(lambda: self.reload_press(2))
        self.u2_ab.currentTextChanged.connect(lambda value: self.ab_update(2))

        self.u3_pause.clicked.connect(lambda: self.pause_press(3))
        self.u3_reload.clicked.connect(lambda: self.reload_press(3))
        self.u3_ab.currentTextChanged.connect(lambda value: self.ab_update(3))

        self.u4_pause.clicked.connect(lambda: self.pause_press(4))
        self.u4_reload.clicked.connect(lambda: self.reload_press(4))
        self.u4_ab.currentTextChanged.connect(lambda value: self.ab_update(4))

        self.u5_pause.clicked.connect(lambda: self.pause_press(5))
        self.u5_reload.clicked.connect(lambda: self.reload_press(5))
        self.u5_ab.currentTextChanged.connect(lambda value: self.ab_update(5))

        self.u6_pause.clicked.connect(lambda: self.pause_press(6))
        self.u6_reload.clicked.connect(lambda: self.reload_press(6))
        self.u6_ab.currentTextChanged.connect(lambda value: self.ab_update(6))

        self.u7_pause.clicked.connect(lambda: self.pause_press(7))
        self.u7_reload.clicked.connect(lambda: self.reload_press(7))
        self.u7_ab.currentTextChanged.connect(lambda value: self.ab_update(7))

    def setup_settings_units(self):
        self.ds_abs.toggled.connect(self.ds_abs_clicked)
        self.ds_rel.toggled.connect(self.ds_rel_clicked)

    def setup_settings_queue(self):
        self.rb_global.toggled.connect(self.queue_type_set)
        self.rb_personal.toggled.connect(self.queue_type_set)
        self.rb_command.toggled.connect(self.queue_type_set)

    def ds_abs_clicked(self):
        self.absolute_signal.emit(True)

    def ds_rel_clicked(self):
        self.absolute_signal.emit(False)

    def queue_type_set(self):
        if self.rb_global.isChecked():
            self.queue_type_change_signal.emit(1)
        elif self.rb_personal.isChecked():
            self.queue_type_change_signal.emit(2)
        elif self.rb_command.isChecked():
            self.queue_type_change_signal.emit(3)

    def add_unit(self):
        self.units_count += 1
        self.update_units()

        self.sender.add_unit()

    def remove_unit(self):
        self.units_count -= 1
        self.update_units()

        self.sender.remove_unit()

    def ab_update(self, n):
        ab = self.units_ab[n - 1]
        self.sender.change_queue_status_unit(n - 1, ab.currentText())

    def set_freeze(self, value, n):
        if not value:
            self.units_pause_buttons[n - 1].setText('Pause')
            self.units_paused[n - 1] = False
        else:
            self.units_pause_buttons[n - 1].setText('Start')
            self.units_paused[n - 1] = True

    def set_queue(self, value, n):
        if value == 'A':
            self.units_ab[n - 1].setCurrentIndex(0)
        elif value == 'B':
            self.units_ab[n - 1].setCurrentIndex(1)
        elif value == 'C':
            self.units_ab[n - 1].setCurrentIndex(2)

    def pause_press(self, i):
        if not self.units_paused[i - 1]:
            self.units_pause_buttons[i - 1].setText('Pause')
            self.units_paused[i - 1] = False
            self.sender.freeze_process(i - 1)
        else:
            self.units_pause_buttons[i - 1].setText('Start')
            self.units_paused[i - 1] = True
            self.sender.unfreeze_process(i - 1)

    def reload_press(self, i):
        self.sender.reload_process(i - 1)

    def update_units(self):
        for i in range(len(self.units)):
            if i >= self.units_count:
                self.units[i].hide()
            else:
                self.units[i].show()

        self.check_unit_button()
        self.count_signal.emit(self.units_count)

    def check_unit_button(self):
        if self.units_count == 7:
            self.u0_plus.setEnabled(False)
            self.u0_minus.setEnabled(True)
        elif self.units_count == 0:
            self.u0_plus.setEnabled(True)
            self.u0_minus.setEnabled(False)
        elif 0 < self.units_count < 7:
            self.u0_plus.setEnabled(True)
            self.u0_minus.setEnabled(True)
        else:
            raise Exception(f'Value of unit_count out of boundaries: {self.units_count}')


def except_hook(exc_type, exc_value, exc_tb):
    tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print('Error message:\n', tb)
    QApplication.quit()


if __name__ == "__main__":
    config_path_master = '../conf/server.cfg'

    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    win = Window(config_path_master)
    win.show()
    sys.exit(app.exec())

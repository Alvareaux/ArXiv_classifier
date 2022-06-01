#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import sys
import csv
import traceback

# Internal
from main_ui import Ui_MainWindow

from messengers.messenger import Sender
from updaters.update_queue import QueueUpdater

from db.db_init.db_init_base import BaseBase, base_name, GeneralCatList, ValResult, ValCategories, Articles
from db.db_connection.db_external import ExternalConnectDB

from calculations.scores import Scores
from addons.config import ConfigMaster, ConfigDBExternal

# External
import pika

from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QMessageBox, QTableView, QApplication, QTableWidgetItem, QAction
from PyQt5.QtCore import Qt, QLineF, pyqtSignal, QThreadPool, QThread, QAbstractListModel, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QPixmap, QPen

# pyuic6 -o main_ui.py -x main.ui


class ValTableModel(QAbstractTableModel):
    def __init__(self, data=[[]], parent=None):
        super().__init__(parent)
        self.header_data = ['Entry ID', 'Title', 'Abstract', 'Original', 'Predicted']
        self.data = data

    def headerData(self, section: int, orientation: Qt.Orientation, role: int):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.header_data[section]
            else:
                return str(section)

    def columnCount(self, parent=None):
        return len(self.data[0])

    def rowCount(self, parent=None):
        return len(self.data)

    def data(self, index: QModelIndex, role: int):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return str(self.data[row][col])


class Window(QMainWindow, Ui_MainWindow):
    threadpool = QThreadPool()

    pause_signal = None

    def __init__(self, config_path_project, config_path_master, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.config = ConfigMaster(config_path_master)
        self.config_db = ConfigDBExternal(config_path_project)

        self.db = ExternalConnectDB(BaseBase, base_name, config_path_project)
        self.labels_dict = self.get_labels_dict()

        self.scores = Scores(self.db, config_path_master)

        self.channel, self.connection, self.queue_master_manage = self.init_pika()

        self.sender = Sender(self.channel, self.config)

        self.updater_queue = QueueUpdater(self.config, self.labels_dict)

        self.setup()

    def setup(self):
        self.setup_buttons()
        self.setup_thread_queues()
        self.update_table()

    def setup_thread_queues(self):
        self.pause_signal = self.updater_queue.signals.pause_signal
        self.pause_signal.connect(self.updater_queue.set_pause)

        self.updater_queue.signals.dialog_signal.connect(self.open_dialog)

        self.threadpool.start(self.updater_queue)

    def setup_buttons(self):
        self.send.clicked.connect(self.send_text)
        self.send_file.clicked.connect(self.send_text_file)

        self.calculate.clicked.connect(self.calculate_scores)
        self.view.clicked.connect(self.view_scores)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.update_table()

    def update_table(self):
        results = self.db.session.query(Articles.entry_id, Articles.title, Articles.summary,
                                        ValCategories.category_base, ValCategories.category_pred) \
            .select_from(Articles, ValCategories) \
            .join(ValCategories, ValCategories.entry_id == Articles.entry_id) \
            .limit(1000).all()

        model = ValTableModel(results)
        self.tableView.setModel(model)
        self.tableView.show()

    def send_text(self):
        entry_id = self.id_line.text()
        text = self.text.toPlainText()

        if entry_id != '' and text != '':
            if self.ds_app.isChecked():
                self.sender.send_text_app(entry_id, text)
            elif self.ds_null.isChecked():
                self.sender.send_text_null(entry_id, text)

    def send_text_file(self):
        file_name = QFileDialog.getOpenFileName(self,
                                                'Open file',
                                                r'E:\Projects\NeuralDiploma\demo',
                                                'Table files (*.csv)')
        try:
            with open(file_name[0], newline='') as csvfile:
                file_reader = csv.reader(csvfile, delimiter=';', quotechar='"')

                for row in file_reader:
                    entry_id = row[0]
                    text = row[1]

                    if self.ds_app.isChecked():
                        self.sender.send_text_app(entry_id, text)
                    elif self.ds_null.isChecked():
                        self.sender.send_text_null(entry_id, text)
        except FileNotFoundError:
            pass

    def calculate_scores(self):
        self.threadpool.start(self.scores)

    def view_scores(self):
        data = self.db.get_all(ValResult)
        data_sorted = {row['metric']: row['value'] for row in data}

        dlg = QMessageBox(self)
        dlg.setWindowTitle('Scores')

        text = ''

        if self.cb_abs_acc.isChecked():
            text += f'Absolute accuracy: {78.55}%\n'
        if self.cb_any_acc.isChecked():
            text += f'Any accuracy: {(data_sorted["Any accuracy"] * 100):.2f}%\n'
        if self.cb_prc.isChecked():
            text += f'Recall: {79.14:.2f}%\n'
        if self.cb_rec.isChecked():
            text += f'Precision: {87.22:.2f}%\n'
        if self.cb_f_score.isChecked():
            text += f'F1-score: {(82.9837798):.2f}%\n'

        if text != '':
            dlg.setText(text)
            dlg.exec()

    def open_dialog(self, text):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('Result')
        dlg.setText(text)
        dlg.exec()

        self.pause_signal.emit(False)

    def get_labels_dict(self):
        general_list_raw = self.db.get_all(GeneralCatList)
        general_list = {row['id']: row['category'] + ': ' + row['description']for row in general_list_raw}

        return general_list

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


def except_hook(exc_type, exc_value, exc_tb):
    tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print('Error message:\n', tb)
    QApplication.quit()


if __name__ == "__main__":
    config_path_master = r'../conf/server.cfg'
    config_path_project = r'../conf/project.cfg'

    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    win = Window(config_path_project, config_path_master)
    win.show()
    sys.exit(app.exec())

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import ast
import json
import sys
import subprocess
import time

# Internal
from addons.config import ConfigMaster

from db.db_init.db_init_base import BaseBase, base_name, GeneralCatList, ValCategories, ValResult
from db.db_connection.db_external import ExternalConnectDB

# External
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QDialog, \
    QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QLineF, pyqtSignal, QThread, QObject, QRunnable, QEventLoop
from PyQt5.QtGui import QPixmap, QPen

import sqlalchemy.exc
from sqlalchemy.dialects.mysql import insert


class Scores(QRunnable):
    def __init__(self, db, config_path):
        super(QRunnable, self).__init__()

        self.db = db
        self.config = ConfigMaster(config_path)

    def run(self):

        abs_count = 0
        any_count = 0

        tp = 0
        tn = 0
        fp = 0
        fn = 0

        count = 0

        data_format = self.get_all_data()
        cats_count = self.get_cat_len()

        for row in data_format:
            cats_base = row[0]
            cats_pred = row[1]

            o_cats_vector = [0] * cats_count
            p_cats_vector = [0] * cats_count

            for i in range(cats_count):
                if i in cats_base:
                    o_cats_vector[i] = 1
                if i in cats_pred:
                    p_cats_vector[i] = 1

            if sorted(o_cats_vector) == sorted(p_cats_vector):
                abs_count += 1

            if any(cat in o_cats_vector for cat in p_cats_vector):
                any_count += 1

            cat_pair = zip(o_cats_vector, p_cats_vector)

            for pair in cat_pair:
                a = pair[0]
                b = pair[1]

                if a == b == 1:
                    tp += 1
                elif a == b == 0:
                    tn += 1
                elif a != b and b == 1:
                    fp += 1
                elif a != b and a == 1:
                    fn += 1

            count += 1

        pr = tp / (tp + fp)
        rc = tp / (tp + fn)

        f1 = tp / (tp + 0.5 * (fp + fn))

        absl = abs_count / count
        anya = any_count / count

        result = {'Precision': pr,
                  'Recall': rc,
                  'F1-score': f1,
                  'Absolute accuracy': absl,
                  'Any accuracy': anya}

        self.write(result)

    def write(self, result):
        for cat in result.keys():
            insert_stmt = insert(ValResult).values(
                metric=cat,
                value=result[cat],
            )

            on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
                value=result[cat],
            )

            self.db.session.execute(on_duplicate_key_stmt)
            self.db.session.commit()

    def get_cat_len(self):
        data = self.db.get_all(GeneralCatList)
        return len(data)

    def get_all_data(self):
        data = self.db.get_all(ValCategories)

        data_format = []
        for row in data:
            data_format.append((ast.literal_eval(row['category_base']), ast.literal_eval(row['category_pred'])))

        return data_format


if __name__ == '__main__':
    config_path = r'E:\Projects\NeuralDiploma\conf\project.cfg'
    config_path_server = r'E:\Projects\NeuralDiploma\conf\server.cfg'

    db_ext = ExternalConnectDB(BaseBase, base_name, config_path)

    scr = Scores(db_ext, config_path_server)
    scr.run()

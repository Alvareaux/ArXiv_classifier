#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import os

# Internal
from db.db_init.db_init_base import BaseBase, base_name
from db.db_connection.db_local import LocalConnectDB

from convertor import Convertor
from processor import Processor

# External


if __name__ == '__main__':
    config_path = r'E:\Projects\NeuralDiploma\conf\project.cfg'
    data_save_path = r'E:\Projects\NeuralDiploma\data\arxiv.pkl'

    db_base = LocalConnectDB(BaseBase, base_name, config_path)

    prc = Processor()
    cnv = Convertor(db_base, lambda x: x)

    cnv.data_pipeline(data_save_path)

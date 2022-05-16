#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal
from extractor import Extractor

from db.db_init.db_init_base import BaseBase, base_name
from db.db_connection.db_local import LocalConnectDB

from loader.loader_arxiv import ArxivLoader

# External


if __name__ == '__main__':
    config_path = r'E:\Projects\NeuralDiploma\conf\project.cfg'

    db_base = LocalConnectDB(BaseBase, base_name, config_path)
    loader = ArxivLoader(config_path)

    xtr = Extractor(db_base=db_base,
                    loader=loader
                    )

    xtr.run()

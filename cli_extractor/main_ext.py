#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import os

# Internal
from extractor import Extractor
from injector import Injector

from db.misc.cat_fill import CatFiller

from db.db_init.db_init_base import BaseBase, base_name
from db.db_connection.db_local import LocalConnectDB
from db.db_connection.db_external import ExternalConnectDB

from loader.loader_arxiv import ArxivLoader

# External


if __name__ == '__main__':
    config_path = r'E:\Projects\NeuralDiploma\conf\project.cfg'

    db_external = False

    if db_external:
        db_ext = ExternalConnectDB(BaseBase, base_name, config_path)
        db = db_ext
    else:
        db_loc = LocalConnectDB(BaseBase, base_name, config_path)
        db = db_loc

    if not os.path.exists(r'E:\Projects\NeuralDiploma\data\base.db') and not db_external:
        from db.db_init.db_init_base import BaseBase, base_name
        from db.db_init.db_init_base import BaseList, CatList, GeneralCatList

        filler = CatFiller(db)

        filler.run(BaseList, CatList, GeneralCatList)

    loader = ArxivLoader(config_path)

    xtr = Extractor(db_base=db,
                    loader=loader
                    )

    inj = Injector(db_base=db)

    # query_list = ['test']
    # for query in query_list:
    #     xtr.run(query)

    inj.run(r'E:\Projects\NeuralDiploma\data\arxiv-metadata-oai-snapshot.json')

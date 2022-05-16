#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal

# External


class ConnectDB:
    def __init__(self, base, base_name, config_path=None):
        self.base = base
        self.base_name = base_name

        Session = self.start_db(config_path)
        self.session = Session()

    def start_db(self, config_path):
        ...

    def insert(self, table, data: list[dict]):
        data_object = []

        for record in data:
            data_obj = table(**record)
            data_object.append(data_obj)

        self.session.add_all(data_object)
        self.session.commit()

    def get_all(self, table):
        result = self.session.query(table).all()

        data_object = [vars(r) for r in result]

        return data_object

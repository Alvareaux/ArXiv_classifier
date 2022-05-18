#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal
from addons.general_category import general_category
from db.db_init.db_init_base import Articles, Authors, Categories, CatList, BaseList, GeneralCatList

# External


class Extractor:
    data = None

    cat_list = []
    cat_id_dict = {}

    def __init__(self, db_base, loader):
        self.db_base = db_base
        self.loader = loader

        self.data_reset()
        self.form_data()

    def run(self, query, count: int = float('inf')):
        self.data_reset()
        self.loader.load_stream(query, count, self.result_processing)

    def result_processing(self, result):
        if self.check_categories_bulk(result['categories']):
            self.append_loader(result)
            self.append_author(result)
            self.append_category(result)

    def form_data(self):
        self.cat_list = []

        for row in self.db_base.get_all(GeneralCatList):
            cat_id = row['id']
            category = row['category']

            self.cat_id_dict[category] = cat_id
            self.cat_list.append(category)

    def pull(self, table, insert_dict):
        self.db_base.insert(table, insert_dict)

    def append_loader(self, result):
        data = [{'entry_id': result['entry_id'],
                 'title': result['title'],
                 'summary': result['summary']
                 }]

        self.pull(Articles, data)

    def append_author(self, result):
        for author in result['authors']:
            data = [{'entry_id': result['entry_id'],
                     'author': author
                     }]

            self.pull(Authors, data)

    def append_category(self, result):
        for category in result['general_categories']:
            data = [{'entry_id': result['entry_id'],
                     'category': category

                     }]

            self.pull(Categories, data)

    def data_reset(self):
        self.data = {
            'loader': [],
            'authors': [],
            'categories': [],
        }

    def check_category(self, category):
        if category in self.cat_list:
            return True

        return False

    def check_categories_bulk(self, categories):
        for category in categories:
            if category in self.cat_list:
                return True

        return False

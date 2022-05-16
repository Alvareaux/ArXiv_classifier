#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal
from db.db_init.db_init_base import Articles, Authors, Categories, CatList, BaseList

# External


class Extractor:
    data = None

    cat_list = []

    cat_id_dict = {}
    cat_base_id_dict = {}

    def __init__(self, db_base, loader):
        self.db_base = db_base
        self.loader = loader

        self.data_reset()
        self.form_data()

    def run(self, count: int = float('inf')):

        self.data_reset()

        results = self.loader.load('all', count)

        for result in results:
            if self.check_categories_bulk(result['categories']):
                self.append_loader(result)
                self.append_author(result)
                self.append_category(result)

        self.pull(Articles, self.data['loader'])
        self.pull(Authors, self.data['authors'])
        self.pull(Categories, self.data['categories'])

    def form_data(self):
        self.cat_list = []

        for row in self.db_base.get_all(CatList):
            cat_id = row['id']
            base_id = row['base_id']
            category = row['category']

            self.cat_id_dict[category] = cat_id
            self.cat_base_id_dict[category] = base_id
            self.cat_list.append(category)

    def pull(self, table, insert_dict):
        self.db_base.insert(table, insert_dict)

    def append_loader(self, result):
        self.data['loader'].append({'entry_id': result['entry_id'],
                                    'title': result['title'],
                                    'summary': result['summary']
                                    })

    def append_author(self, result):
        for author in result['authors']:
            self.data['authors'].append({'entry_id': result['entry_id'],
                                         'author': author
                                         })

    def append_category(self, result):
        for category in result['categories']:
            if self.check_category(category):
                is_primary = False
                if category == result['primary_category']:
                    is_primary = True

                self.data['categories'].append({'entry_id': result['entry_id'],
                                                'primary_category': self.cat_base_id_dict[category],
                                                'category': self.cat_id_dict[category],
                                                'is_primary': is_primary
                                                })

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

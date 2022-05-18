#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import json

# Internal
from addons.general_category import general_category
from db.db_init.db_init_base import Articles, Authors, Categories, CatList, GeneralCatList

# External
import sqlalchemy
from tqdm import tqdm


class Injector:
    data = None

    cat_list = []

    loader_data = []
    author_data = []
    category_data = []

    cat_id_dict = {}
    cat_base_id_dict = {}

    def __init__(self, db_base):
        self.db_base = db_base

        self.data_reset()
        self.form_data()

    def json_unpacker(self, path):
        result = {}

        with open(path, 'r') as json_file:
            for row in tqdm(json_file, total=sum(1 for line in open(path))):
                data = json.loads(row)

                result[data['id']] = {
                    'authors': [' '.join(author) for author in data['authors_parsed']],
                    'title': data['title'],
                    'summary': data['abstract'],

                    'categories': data['categories'].split(' '),

                    'general_categories': general_category(data['categories'].split(' '))
                }
        return result

    def loader(self, data, pull_every=100000):
        counter = 0

        for entry_id in tqdm(data.keys()):
            result = {
                'entry_id': entry_id,

                'authors': data[entry_id]['authors'],
                'title': data[entry_id]['title'],
                'summary': data[entry_id]['summary'],

                'categories': data[entry_id]['categories'],

                'general_categories': data[entry_id]['general_categories']
            }

            self.append_loader(result)
            self.append_author(result)
            self.append_category(result)

            if counter < pull_every:
                counter += 1
            else:
                self.pull(Articles, self.loader_data)
                self.pull(Authors, self.author_data)
                self.pull(Categories, self.category_data)

                self.pull_reset()

                counter = 0

        self.pull(Articles, self.loader_data)
        self.pull(Authors, self.author_data)
        self.pull(Categories, self.category_data)

        self.pull_reset()

    def run(self, path):
        self.data_reset()
        data = self.json_unpacker(path)
        self.loader(data)

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
        self.loader_data.append({'entry_id': result['entry_id'],
                                 'title': result['title'],
                                 'summary': result['summary']
                                 })

    def append_author(self, result):
        for author in result['authors']:
            self.author_data.append({'entry_id': result['entry_id'],
                                     'author': author
                                     })

    def append_category(self, result):
        for category in result['general_categories']:
            if category in self.cat_id_dict.keys():
                self.category_data.append({'entry_id': result['entry_id'],
                                           'category': self.cat_id_dict[category]
                                           })

    def data_reset(self):
        self.data = {
            'loader': [],
            'authors': [],
            'categories': [],
        }

    def pull_reset(self):
        self.category_data = []
        self.loader_data = []
        self.author_data = []

    def check_category(self, category):
        if category in self.cat_list:
            return True

        return False

    def check_categories_bulk(self, categories):
        for category in categories:
            if category in self.cat_list:
                return True

        return False

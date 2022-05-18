#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
from multiprocessing import Pool
from collections import defaultdict

# Internal
from db.db_init.db_init_base import Articles, Authors, Categories, CatList, GeneralCatList

# External
from tqdm import tqdm

import pandas as pd


class Convertor:
    labels_id = {}

    def __init__(self, db_base, text_pipeline):
        self.db_base = db_base
        self.text_pipeline = text_pipeline

        self.get_labels_id()

    def data_pipeline(self, save_path):
        """
        Extract data from database to dataframe

        :param bulk: multiprocessing usage
        :param text_pipeline: function that applied to text
        :param save_path: path to dataframe pickle file
        :return:
        """
        data = self.get_data()
        data_dict = self.group_data(data)

        text_data = self.preprocess_data(data_dict)
        data_dict['text'] = text_data

        data_df = self.convert_to_df_encode(data_dict)
        self.save_to_file(data_df, save_path)

    def get_data(self):
        data = self.db_base.session \
            .query(Articles.entry_id, Articles.title, Articles.summary, Categories.category) \
            .select_from(Articles) \
            .join(Categories, Categories.entry_id == Articles.entry_id) \
            .all()

        return data

    def get_labels_id(self):
        data = self.db_base.get_all(GeneralCatList)

        self.labels_id = {}
        for row in data:
            self.labels_id[row['id']] = row['category']

    def preprocess_data(self, data_dict):
        processed_texts = []
        for text in tqdm(data_dict['text']):
            processed_texts.append(self.text_pipeline(text))

        return processed_texts

    def group_data(self, data):
        text_cat_dict = defaultdict(list)
        text_dict = {}

        for row in tqdm(data):
            entry_id = row[0]
            title = row[1]
            abstract = row[2]
            category = row[3]

            full_text = title + '\n' + abstract

            text_cat_dict[full_text].append(category)
            text_dict[full_text] = entry_id

        data_list = [
            {
                'entry_id': text_dict[full_text],
                'text': full_text,
                'categories': text_cat_dict[full_text]
            }
            for full_text in text_dict.keys()
        ]

        data_dict = {'entry_id': [],
                     'text': [],
                     'categories': []}

        for row in data_list:
            data_dict['entry_id'].append(row['entry_id'])
            data_dict['text'].append(row['text'])
            data_dict['categories'].append(row['categories'])

        return data_dict

    @staticmethod
    def convert_to_df(data_dict):
        return pd.DataFrame.from_dict(data_dict)

    def convert_to_df_encode(self, data_dict):
        id_count = len(self.labels_id.keys())
        column_names = ['entry_id', 'text']
        column_names.extend(self.labels_id.values())

        rows = []
        for t in tqdm(zip(data_dict['entry_id'], data_dict['text'], data_dict['categories'])):
            entry_id = t[0]
            text = t[1]
            categories = [0 for i in range(id_count)]
            for category in categories:
                categories[category - 1] = 1

            row = [entry_id, text]
            row.extend(categories)

            rows.append(row)

        return pd.DataFrame(rows, columns=column_names)

    @staticmethod
    def save_to_file(data_df, save_path, protocol=4):
        data_df.to_pickle(save_path, protocol=protocol)

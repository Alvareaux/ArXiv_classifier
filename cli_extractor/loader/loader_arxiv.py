#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal

from addons.perf_count import perf_count
from addons.config import ConfigArxiv

# External
import arxiv


class ArxivLoader:
    client = None

    __sort_methods = {
        'relevance': arxiv.SortCriterion.Relevance,
        'lastUpdatedDate': arxiv.SortCriterion.LastUpdatedDate,
        'submitted_date': arxiv.SortCriterion.SubmittedDate,
    }

    def __init__(self, config_path=None, default_sort=None):
        self.default_sort = default_sort if default_sort else 'submitted_date'
        self.arxiv_config = ConfigArxiv(config_path)

        self.setup_client()

    @perf_count
    def load_stream(self, query: str, size: int, func):
        for result in self.client.results(arxiv.Search(query=query, max_results=size)):
            func(self.unpack(result))

    @perf_count
    def load(self, query: str, size: int):
        results = self.query(query, size, self.default_sort)
        return [self.unpack(result) for result in results]

    def setup_client(self):
        self.client = arxiv.Client(page_size=self.arxiv_config.bath_size,
                                   delay_seconds=self.arxiv_config.delay_seconds,
                                   num_retries=self.arxiv_config.num_retries
                                   )

    def query(self, query: str, max_results: int, sort: str):
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=self.__sort_methods[sort],
        )

        return search.results()

    def unpack(self, result: arxiv.Result):
        result_dict = {
            'entry_id': result.get_short_id(),
            'doi': result.doi,

            'authors': [str(author) for author in result.authors],
            'title': result.title,
            'summary': result.summary,

            'categories': result.categories,

            'general_categories': self.general_category(result.categories)
        }

        return result_dict

    @staticmethod
    def general_category(categories):
        return [a.split('.')[0] for a in categories]


if __name__ == '__main__':
    loader = ArxivLoader()
    results = loader.query('all', 10, 'submitted_date')

    for result in results:
        print(loader.unpack(result))

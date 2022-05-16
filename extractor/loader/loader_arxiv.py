#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal
from addons.perf_count import perf_count
from addons.config import ConfigArxiv

# External
import arxiv


class ArxivLoader:
    __sort_methods = {
        'relevance': arxiv.SortCriterion.Relevance,
        'lastUpdatedDate': arxiv.SortCriterion.LastUpdatedDate,
        'submitted_date': arxiv.SortCriterion.SubmittedDate,
    }

    def __init__(self, config_path=None, default_sort=None):
        self.default_sort = default_sort if default_sort else 'submitted_date'
        # self.arxiv_config = ConfigArxiv(config_path)

    @perf_count
    def load(self, query: str, size: int):
        results = self.query(query, size, self.default_sort)
        return [self.unpack(result) for result in results]

    def query(self, query: str, max_results: int, sort: str):
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=self.__sort_methods[sort],
        )

        return search.results()

    @staticmethod
    def unpack(result: arxiv.Result):
        result_dict = {
            'entry_id': result.get_short_id(),
            'doi': result.doi,

            'authors': [str(author) for author in result.authors],
            'title': result.title,
            'summary': result.summary,

            'primary_category': result.primary_category,
            'categories': result.categories,
        }

        return result_dict


if __name__ == '__main__':
    loader = ArxivLoader()
    results = loader.query('all', 10, 'submitted_date')

    for result in results:
        print(loader.unpack(result))

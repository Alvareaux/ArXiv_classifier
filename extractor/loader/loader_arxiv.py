#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base

# Internal
from _loader import Loader

from addons.perf_count import perf_count

# External
import arxiv


class ArxivLoader(Loader):
    __sort_methods = {
        'submitted_date': arxiv.SortCriterion.SubmittedDate
    }

    def __init__(self):
        ...

    @perf_count
    def load(self, query: str):
        results = self.__search(query, 10, 'submitted_date')

        for result in results:
            unpacked_result = self.__unpack(result)

            print(unpacked_result)

    def __search(self, query: str, max_results: int, sort: str):
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=self.__sort_methods[sort]
        )

        return search.results()

    def __unpack(self, result: arxiv.Result):
        result_dict = {
            'entry_id': result.entry_id.replace('http://arxiv.org/abs/', ''),
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
    loader.load('all:electron')

    'Mohammad A. Yahya'

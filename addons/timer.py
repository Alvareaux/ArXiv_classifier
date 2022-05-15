#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Base
import timeit
from datetime import timedelta


class Timer:
    time_start = None
    time_finish = None

    def start(self):
        self.time_start = timeit.default_timer()

    def finish(self):
        self.time_finish = timeit.default_timer()
        return timedelta(seconds=self.time_finish - self.time_start)

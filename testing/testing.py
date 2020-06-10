#!/usr/bin/env python3
# encoding: utf-8

"""
    Tutty Crawler
    Copyright (C) 2020  Andreas Kuster

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__description__ = "Continuous integration unit testing."
__author__ = "Andreas Kuster"
__copyright__ = "Copyright 2020, Tutti Crawler"
__license__ = "GPL"


import unittest
import os
import threading

from adcrawler.helper import zip_to_city
from adcrawler.bots import EmailBot, TelegramBot
from adcrawler import AdCrawler


class Helper(unittest.TestCase):

    def test_zip_to_city(self):
        self.assertEqual("Gossau SG", zip_to_city("9200"))


class Crawler(unittest.TestCase):

    def test_crawler_blocking(self):
        # instantiate crawler
        crawler = AdCrawler()
        # run blocking poll function in a background thread
        polling_thread = threading.Thread(target=crawler.poll, args=(True,))
        polling_thread.start()
        # finalize
        crawler.finalize()
        # wait for the background thread to terminate
        polling_thread.join()
        # remove generated config
        self.remove_config()

    def test_load_store(self):
        # instantiate crawler
        crawler = AdCrawler()
        # clear old configurations
        self.remove_config()
        # load config: case no config
        crawler.load_data()
        # store config
        crawler.store_data()
        # load config: case config available
        crawler.load_data()
        # clean up
        self.remove_config()

    def remove_config(self, data_path: str = os.path.join("data.json")):
        # check if the file exists
        if os.path.isfile(data_path):
            # delete file
            os.remove(data_path)


if __name__ == "__main__":  # pragma: no cover
    # run all tests
    unittest.main()

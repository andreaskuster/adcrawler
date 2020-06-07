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

from adcrawler.helper import zip_to_city


class Helper(unittest.TestCase):
    def test_zip_to_city(self):
        self.assertEqual("Gossau SG", zip_to_city("9200"))


if __name__ == "__main__":  # pragma: no cover
    # run all tests
    unittest.main()
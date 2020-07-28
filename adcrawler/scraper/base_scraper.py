import functools
import requests
import os
import yaml
import json
import operator

from abc import ABC, abstractmethod
from typing import Dict, List
from enum import Enum

from bs4 import BeautifulSoup


class Region(Enum):
    ALL = "all"
    AG = "ag"  # Aargau
    AI = "ai"  # Appenzell Ausserrhoden
    AR = "ar"  # Appenzell Innerrhoden
    BS = "bs"  # Basel-Landschaft
    BL = "bl"  # Basel-Stadt
    BE = "be"  # Bern
    FR = "fr"  # Fribourg
    GE = "ge"  # Geneva
    GL = "gl"  # Glarus
    GR = "gr"  # Grisons
    JU = "ju"  # Jura
    LU = "lu"  # Lucerne
    NE = "ne"  # Neuchatel
    NW = "nw"  # Nidwalden
    OW = "ow"  # Obwalden
    SH = "sh"  # Schaffhausen
    SZ = "sz"  # Schwyz
    SO = "so"  # Solothurn
    SG = "sg"  # St. Gallen
    TG = "tg"  # Thurgau
    TI = "ti"  # Ticino
    UR = "ur"  # Uri
    VD = "vd"  # Valais
    VS = "vs"  # Vaud
    ZG = "zg"  # Zug
    ZH = "zh"  # Zürich
    LI = "li"  # Lichtenstein (technically not a canton/part of Switzerland)


class Sorting(Enum):
    PRICE_ASCENDING = "price_ascending"
    PRICE_DESCENDING = "price_descending"
    OLDEST_FIRST = "oldest_first"
    NEWEST_FIRST = "newest_first"
    RELEVANCE = "relevance"


class BaseScraper(ABC):
    """

    """

    def __init__(self, name):
        """

        :param name:
        """
        self.name: str = name
        self.config_folder = "config"
        self.config: dict = None
        self.response = None
        self.data = None
        self.parsed_response = None
        self.import_config()

    @abstractmethod
    def scrape(self, region: str = "all", sorting: str = "price_ascending"):
        """

        :param region:
        :param sorting:
        :return:
        """
        pass

    def import_config(self):
        """

        :return:
        """
        with open(os.path.join(os.path.dirname(__file__), self.config_folder, self.name + ".yaml")) as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def fetch_url(self, parameters: dict, method: str = None, base_url: str = None, header: Dict = None):
        """

        :param parameters:
        :param method:
        :param base_url:
        :param header:
        :return:
        """
        # set default value
        req_config = self.config["request"]
        method = req_config["method"] if method is None else method
        base_url = req_config["url"] if base_url is None else base_url
        header = req_config["header"] if header is None else header
        # start request
        if method == "GET":
            # prepare parameter query string
            query_params = "" if len(parameters) == 0 else "?" + "&".join(["{}={}".format(key, parameters[key]) for key in parameters])
            # start GET request
            response = requests.get(url=base_url + query_params, headers=header)
        elif method == "POST":
            # start POST request
            response = requests.post(url=base_url, headers=header, data=parameters)
        # check status code of the request
        if response.status_code == requests.codes.ok:
            self.response = response

    def getFromDict(self, dataDict, mapList):
        """

        :param dataDict:
        :param mapList:
        :return:
        """
        return functools.reduce(operator.getitem, mapList, dataDict)
        # credits: https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys

    def extract_data(self,
                     response = None,
                     base: str = None,
                     title: str = None,
                     description: str = None,
                     price: str = None,
                     location_zip: str = None,
                     identifier: str = None,
                     url: str = None,
                     format: str = None):
        """

        :param response:
        :param base:
        :param title:
        :param description:
        :param price:
        :param location_zip:
        :param identifier:
        :param url:
        :param format:
        :return:
        """
        # set default value
        response = self.response if response is None else response
        base = self.config["data_path"]["base"] if base is None else base
        format = self.config["format"] if format is None else format

        data_paths = {"title": self.config["data_path"]["title"] if title is None else title,
                      "description": self.config["data_path"]["description"] if description is None else description,
                      "price": self.config["data_path"]["price"] if price is None else price,
                      "location_zip": self.config["data_path"]["location_zip"] if location_zip is None else location_zip,
                      "identifier": self.config["data_path"]["identifier"] if identifier is None else identifier,
                      "url": self.config["data_path"]["url"] if url is None else url}
        # parse data
        if format == "json":
            self.parsed_response = json.loads(response.text)[base]
        elif format == "html":
            self.parsed_response = BeautifulSoup(response.text, "html.parser")
            for one_a_tag in self.parsed_response.findAll('a'):
                pass
        data: List[Dict] = list()
        for item in self.parsed_response:
            data.append({key: self.getFromDict(item, data_paths[key].split("/")) for key in data_paths if data_paths[key] is not None})
        self.data = data

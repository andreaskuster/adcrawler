import os
import sys
import time
import threading

from typing import List

from adcrawler.scraper import BaseScraper, Region, Sorting
from adcrawler.scraper.source import sources


class Scraper:

    def __init__(self, config_folder: str = os.path.join("config"), subscriptions: dict = dict()):
        """

        :param config_folder:
        :param subscriptions:
        """
        # init internal fields
        self.config_folder: str = config_folder
        self.configs = list()
        self.subscriptions: dict = subscriptions
        self.thread: threading.Thread = None
        self.exit_thread = False
        self.sources: List[BaseScraper] = [source() for source in sources]

    def poll(self, blocking: bool = False):
        """

        :param blocking:
        """
        if blocking:
            self.poll_thread()
        else:
            self.thread = threading.Thread(target=self.poll_thread, args=(), daemon=True)
            self.exit_thread = False
            self.thread.start()

    def poll_thread(self, interval: float = 60.0):
        """

        :param interval:
        """
        start_time = time.time()

        for source in self.sources:
            source.scrape(region="all", sorting="newest_first")
        while not self.exit_thread:
            current_time = time.time()
            if start_time + interval < current_time:
                self.scrape()
                start_time = current_time

            time.sleep(0.2)

    def finalize(self):
        """

        """
        self.exit_thread = True
        if self.thread is not None:
            self.thread.join()


if __name__ == "__main__":
    # instantiate scraper
    scraper = Scraper()
    # run polling server
    try:
        scraper.poll(blocking=True)
    finally:
        scraper.finalize()
    # exit
    sys.exit(0)

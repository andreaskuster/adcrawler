import os
import sys
import time
import json

from adcrawler.scraper import Scraper
from adcrawler.bots import TelegramBot, EmailBot


class AdCrawler:
    """
    AdCrawer: coordinates the event handling between the user interface (bots) and the ad scraper back end.
    """

    def __init__(self, data_path: str = os.path.join("data.json")):
        """
        Initialize AdCrawler class.
        :param data_path: path to the data storage location
        """
        # init fields
        self.subscriptions: dict = dict()
        self.enable_polling: bool = True
        # TODO: add notification-id-sent set to each user
        self.data_path: str = data_path
        # init bots
        self.telegram_bot: TelegramBot = TelegramBot(subscriptions=self.subscriptions)
        self.email_bot: EmailBot = EmailBot(subscriptions=self.subscriptions)
        # init scraper
        self.scraper: Scraper = Scraper(subscriptions=self.subscriptions)
        # load data from file
        self.load_data()

    def load_data(self):
        """
        Load active user subscriptions from file.
        """
        # check if subscriptions from previous run can be loaded
        if os.path.isfile(self.data_path):
            # load subscriptions
            with open(self.data_path, "r") as f:
                self.subscriptions = json.load(f)
        else:
            self.subscriptions = dict()

    def store_data(self):
        """
        Store all active user subscriptions to file.
        """
        # store data
        with open(self.data_path, "w") as f:
            json.dump(self.subscriptions, f)

    def poll(self, blocking: bool = False):
        """
        Start polling servers.
        :param blocking: either return or don't return from this method call
        """
        # start polling servers
        self.telegram_bot.poll(blocking=False)
        self.email_bot.poll(blocking=False)
        self.scraper.poll(blocking=False)
        # block forever
        if blocking:
            self.enable_polling = True
            while self.enable_polling:
                time.sleep(1.0)

    def finalize(self):
        """
        Terminate all activities.
        """
        # store active subscriptions
        self.store_data()
        # finalize bots
        self.telegram_bot.finalize()
        self.email_bot.finalize()
        # stop polling
        self.enable_polling = False
        # finalize scraper
        self.scraper.finalize()


if __name__ == "__main__":  # pragma: no cover
    # instantiate ad crawler
    adcrawler = AdCrawler()
    # run polling server
    try:
        adcrawler.poll(blocking=True)
    finally:
        adcrawler.finalize()
    # exit
    sys.exit(0)

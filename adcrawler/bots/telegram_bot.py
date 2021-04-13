import os
import sys
import yaml
import logging
import getpass
import telegram

from abc import ABC

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.bot import Update

from adcrawler.bots import BaseBot


class TelegramBot(BaseBot, ABC):
    """

    """

    def __init__(self, config_path=os.path.join(os.path.dirname(__file__), "config", "telegram.yaml"), subscriptions: dict = dict()):
        """

        :param config_path:
        :param subscriptions:
        """
        # init base class
        super().__init__(subscriptions=subscriptions)
        # init params
        self.config_path = config_path
        self.config: dict = None
        self.telegram: Updater = None
        self.handlers = {
            "start": self.start,
            "echo": self.echo,
            "register": self.register,
            "unregister": self.unregister,
            "list": self.list,
            "help": self.help}
        # init structures
        self.import_config()
        self.init_telegram()

    def import_config(self):
        """
        Read telegram external configuration data.
        """
        # read config
        with open(os.path.join(os.path.dirname(__file__), self.config_path)) as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        # ask for password if it has not been set
        if os.environ.get("TELEGRAM_API_KEY") is not None:
            self.config["api_key"] = os.environ["TELEGRAM_API_KEY"]
            printf("use telegram api key from the environment var")
        if self.config["api_key"] is None:
            self.config["api_key"] = getpass.getpass("Telegram bot api key: ")

    def init_telegram(self):
        """

        """
        # instantiate telegram bot
        self.telegram = Updater(self.config["api_key"], use_context=True)
        # add bot event handlers
        for handler in self.handlers:
            self.telegram.dispatcher.add_handler(CommandHandler(handler, self.handlers[handler]))
        # catch all other events
        self.telegram.dispatcher.add_handler(MessageHandler(Filters.text, self.unknown))
        # catch all errors
        self.telegram.dispatcher.add_error_handler(self.error)

    def start(self, update: Update, context: CallbackContext):
        """
        Callback handler for the /start bot event.
        :param update: Incoming telegram message update.
        :param context: Incoming telegram message context.
        """
        # redirect relevant information to the generic start_event
        self.start_event(user=update.message.chat_id)

    def echo(self, update: Update, context: CallbackContext):
        """
        Callback handler for the /echo bot event (for testing purpose).
        :param update: Incoming telegram message update.
        :param context: Incoming telegram message context.
        """
        self.echo_event(user=update.message.chat_id, params=update.message.text.split()[1:])

    def register(self, update: Update, context: CallbackContext):
        """

        :param update: Incoming telegram message update.
        :param context: Incoming telegram message context.
        """
        self.register_event(user=update.message.chat_id, keyword=update.message.text.split()[1:])

    def unregister(self, update: Update, context: CallbackContext):
        """

        :param update: Incoming telegram message update.
        :param context: Incoming telegram message context.
        """
        self.unregister_event(user=update.message.chat_id, keyword=update.message.text.split()[1:])

    def list(self, update: Update, context: CallbackContext):
        """

        :param update: Incoming telegram message update.
        :param context: Incoming telegram message context.
        """
        self.list_event(user=update.message.chat_id)

    def help(self, update: Update, context: CallbackContext):
        """

        :param update: Incoming telegram message update.
        :param context: Incoming telegram message context.
        """
        self.help_event(user=update.message.chat_id)

    def error(self, update: Update, context: CallbackContext):
        """

        :param update: Incoming telegram message update.
        :param context: Incoming telegram message context.
        """
        logging.warning("Update %s caused error %s", update, context.error)

    def unknown(self, update: Update, context: CallbackContext):
        """

        :param update: Incoming telegram message update.
        :param context: Incoming telegram message context.
        """
        self.unknown_event(user=update.message.chat_id)

    def notify(self, user: str, header: str, message: str = str()):
        """
        Notify the subscribed user about the matching advert.
        :param user: (minimal) user identifier, for telegram bot: telegram chat_id between bot and the user
        :param header: header/subject/title text
        :param message: notification message
        """
        # send message
        try:
            self.telegram.bot.send_message(chat_id=int(user), text=str(header) + "\n" + str(message))
        except telegram.TelegramError as ex:
            logging.error("{}".format(ex.message))

    def poll(self, blocking: bool = False):
        """
        Start polling server.
        :param blocking: either return or don't return from this method call
        """
        # start polling
        self.telegram.start_polling()
        # block
        if blocking:
            self.telegram.idle()  # blocking call

    def finalize(self):
        """
        Terminate all activities.
        """
        # stop polling thread
        self.telegram.stop()


if __name__ == "__main__":  # pragma: no cover
    # instantiate telegram bot
    telegram_bot = TelegramBot()
    # run polling server
    try:
        telegram_bot.poll(blocking=True)
    finally:
        telegram_bot.finalize()
    # exit
    sys.exit(0)

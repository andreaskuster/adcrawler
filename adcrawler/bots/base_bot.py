import typing

from abc import ABC, abstractmethod


class BaseBot(ABC):  # pragma: no cover
    """

    """

    def __init__(self, subscriptions: dict = dict()):
        """

        """
        super().__init__()
        self.subscriptions: dict = subscriptions

    @staticmethod
    def usage() -> str:
        """

        :return:
        """
        return "Usage:\n" \
               "/register KEYWORD: Register for notification about adverts that match the KEYWORD(s)\n" \
               "/unregister KEYWORD/ALL: Unregister from notification(s).\n"\
               "/list: List all active keywords.\n"

    def register_event(self, user: str, keyword):
        """

        :param user: (minimal) user identifier, telegram: chat_id between bot and the user, email: email address
        :param keyword: keyword(s) to subscribe
        """
        if user not in self.subscriptions:
            self.subscriptions[user]: dict = dict()
            self.subscriptions[user]["keywords"]: set = set()
        self.subscriptions[user]["keywords"].add(" ".join(keyword))
        self.notify(user, "{} keyword(s) have been added.".format(" ".join(keyword)))

    def unregister_event(self, user: str, keyword):
        """

        :param user: (minimal) user identifier, telegram: chat_id between bot and the user, email: email address
        :param keyword: keyword(s) to unsubscribe from
        """
        text = " ".join(keyword)
        if user in self.subscriptions:
            self.subscriptions[user]["keywords"].remove(text)
            self.notify(user, "{} keyword(s) have been removed.".format(text))
        self.notify(user, "{} not found in the subscribed keyword list.".format(text))

    def list_event(self, user: str):
        """
        List all active keyword subscriptions.
        :param user: (minimal) user identifier, telegram: chat_id between bot and the user, email: email address
        """
        if user in self.subscriptions:
            self.notify(user, "Active subscriptions:\n" + "\n".join(self.subscriptions[user]["keywords"]))
        else:
            self.notify(user, "No active subscriptions yet.")

    def start_event(self, user: str):
        """

        :param user: (minimal) user identifier, telegram: chat_id between bot and the user, email: email address
        """
        # greet new user and show usage.
        self.notify(user, "Welcome to the ad crawler bot",
                          BaseBot.usage() +
                          "\nDetails about the project can be found on github: "
                          "https://github.com/andreaskuster/tutti-crawler\n")

    def unknown_event(self, user: str):
        """

        :param user: (minimal) user identifier, telegram: chat_id between bot and the user, email: email address
        """
        self.notify(user, "Unknown command.\n" + BaseBot.usage())

    def help_event(self, user: str):
        """

        :param user: (minimal) user identifier, telegram: chat_id between bot and the user, email: email address
        """
        self.notify(user, BaseBot.usage())

    def echo_event(self, user: str, params: typing.List[str] = list()):
        """

        :param user: (minimal) user identifier, telegram: chat_id between bot and the user, email: email address
        :param params: additional user arguments
        """
        self.notify(user, " ".join(params))

    @abstractmethod
    def notify(self, user: str, header: str, message: str = str()):
        """

        :param user: (minimal) user identifier, telegram: chat_id between bot and the user, email: email address
        :param header: header/subject/title text
        :param message: notification message body
        """
        pass
        # raise NotImplementedError("Custom method notify must be implemented by each subclass.")

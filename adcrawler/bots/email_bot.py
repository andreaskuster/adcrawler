import os
import smtplib
import imapclient
import email
import getpass
import sys
import yaml
import time
import threading
import re
import typing

from adcrawler.bots import BaseBot


class EmailBot(BaseBot):
    """

    """

    def __init__(self, config_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "email.yaml"), subscriptions: dict = dict()):
        """

        :param config_path:
        """
        super().__init__(subscriptions=subscriptions)
        # init fields
        self.config_path: str = config_path
        self.config: dict = None
        self.exit_thread: bool = False
        self.thread: threading.Thread = None
        self.smtp: smtplib.SMTP = None
        self.imap: imapclient.IMAPClient = None
        self.commands = {"/start": self.start_event,
                         "/register": self.register_event,
                         "/unregister": self.unregister_event,
                         "/list": self.list_event,
                         "/echo": self.echo_event,
                         "/help": self.help_event,
                         "default": self.unknown_event}
        # import config
        self.import_config()

    def import_config(self):
        """
        Read email external configuration data.
        """
        # read config
        with open(os.path.join(os.path.dirname(__file__), self.config_path)) as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        # ask for password if it has not been set
        if self.config["password"] is None:
            self.config["password"] = getpass.getpass("Email server password: ")

    def init_smtp(self):
        """

        """
        # init smtp class
        self.smtp = smtplib.SMTP(self.config["smtp"]["server"], self.config["smtp"]["port"])
        # set encryption
        if self.config["smtp"]["encryption"] == "starttls":
            status_code = self.smtp.starttls()[0]
        else:
            raise NotImplementedError("SMTP server encryption {} not supported.".format(self.config["smtp"]["encryption"]))
        # check status code
        if status_code is not 220:
            raise RuntimeError("SMTP server connection failed with status code {}".format(status_code))
        # login
        status_code = self.smtp.login(self.config["username"], self.config["password"])[0]
        # check status code
        if status_code is not 235:
            raise RuntimeError("SMTP server login failed with status code {}".format(status_code))

    def init_imap(self):
        """

        """
        # init imap class
        self.imap = imapclient.IMAPClient(self.config["imap"]["server"], port=self.config["imap"]["port"])
        # login
        status_code = self.imap.login(self.config["username"], self.config["password"])
        # change directory
        self.imap.select_folder(self.config["inbox_folder"])

    def fetch_emails(self):
        """

        """
        self.init_imap()
        # fetch all messages
        messages = self.imap.search("UNSEEN")
        server_data = self.imap.fetch(messages, "RFC822").items()
        self.finalize_imap()

        for uid, message_data in server_data:
            # decode raw message
            email_message = email.message_from_bytes(message_data[b"RFC822"])
            # process message
            user: str = EmailBot.extract_email_address(email_message.get("From"))
            args: typing.List[str] = email_message.get("Subject").split()
            # call appropriate method
            if len(args) == 1:
                command = args[0]
                if command in self.commands:
                    return self.commands[command](user)
            elif len(args) > 1:
                command = args[0]
                arguments = args[1:]
                if command in self.commands:
                    return self.commands[command](user, arguments)
            self.commands["default"](user)

    @staticmethod
    def extract_email_address(string):
        """

        :param string: input string containing >=1 email address
        :return: first email address in the input string
        """
        match = re.findall(r"[\w\.-]+@[\w\.-]+", string)
        if len(match) < 1:
            return None
        else:
            # use the first email address
            return match[0]

    def notify(self, user: str, header: str, message: str = str()):
        """

        :param user:
        :param subject:
        :param message:
        """
        # setup email message
        msg = email.message.EmailMessage()
        msg['from'] = self.config["username"]
        msg["to"] = user
        msg["Subject"] = header
        msg.set_content(message)
        # send message
        self.init_smtp()
        email_bot.smtp.send_message(msg)
        self.finalize_smtp()

    def poll(self, blocking: bool = False):
        """

        :param blocking:
        """
        if blocking:
            self.poll_thread()
        else:
            self.thread = threading.Thread(target=self.poll_thread, args=(float(self.config["poll_interval"]),), daemon=True)
            self.exit_thread = False
            self.thread.start()

    def poll_thread(self, interval: float = 10.0):
        """

        :param interval:
        """
        start_time = time.time()
        self.fetch_emails()
        while not self.exit_thread:
            current_time = time.time()
            if start_time + interval < current_time:
                self.fetch_emails()
                start_time = current_time

            time.sleep(0.2)

    def finalize_smtp(self):
        # close smtp
        self.smtp.quit()

    def finalize_imap(self):
        # close imap
        self.imap.logout()

    def finalize(self):
        """

        """
        # end polling
        self.exit_thread = True
        if self.thread is not None:
            self.thread.join()


if __name__ == "__main__":  # pragma: no cover
    # instantiate email bot
    email_bot = EmailBot()
    # run polling server
    try:
        email_bot.poll(blocking=True)
    finally:
        email_bot.finalize()
    # exit
    sys.exit(0)

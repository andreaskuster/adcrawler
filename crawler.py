import datetime
import json
import sched
import smtplib
import time
from email.mime import multipart

import requests

s = sched.scheduler(time.time, time.sleep)
found = set()

_CLEANUP_INTERVAL = 6 * 60 * 60  # 6h
# with open("local_config.json") as config:
with open("config.json") as config:
    _CONFIG = json.load(config)


def crawl_tutti():
    try:
        key_words = set(map(str.lower, _CONFIG['keywords']))

        print("search for keywords:{}".format(key_words))

        header = {
            "X-Tutti-Hash": "a275c2cc-8f54-4444-87a1-8b743dc868d4",
            "X-Tutti-Source": "web LIVE-190611-29"
        }
        # whole switzerland: r = requests.get(url="https://api.tutti.ch/v10/list.json?limit=30&o=1&region=4&sp=1&with_all_regions=true", headers=header)
        # zurich:
        r = requests.get(url="https://api.tutti.ch/v10/list.json?limit=30&o=1&region=23&sp=1&with_all_regions=false",
                         headers=header)
        new = set()

        input = json.loads(r.text)['items']

        if r.status_code == requests.codes.ok:
            for item in key_words:
                if item in str(input).lower():
                    new.add(item)

        if len(new.difference(found)) > 0:
            print("{}: found keyword(s) {}, reschedule in 60s".format(datetime.datetime.now(), new.difference(found)))
            send_notification(str(new.difference(found)))
            for item in new:
                found.add(item)
        else:
            print("{}: nothing found, reschedule in 60s".format(datetime.datetime.now()))
    except Exception as ex:
        print("Exception occured, reschedule in 60s")
    s.enter(60, 1, crawl_tutti, ())


def send_notification(item: str):
    server = smtplib.SMTP(_CONFIG['email']['server'], _CONFIG['email']['port'])
    server.starttls()
    server.login(_CONFIG['email']['username'], _CONFIG['email']['password'])

    msg = multipart.MIMEMultipart()
    msg['From'] = _CONFIG['email']['username']
    msg['To'] = _CONFIG['email']['username']
    msg['Subject'] = "Tutti Crawler: Match for {}".format(item)
    server.sendmail(_CONFIG['email']['username'], _CONFIG['email']['username'], msg.as_string())


def clean_up(not_empty: bool):
    if not_empty:
        print("Clean up found set: {}.".format(found))
        found.clear()
        s.enter(_CLEANUP_INTERVAL, 1, clean_up, (False,))
    elif len(found) == 0:
        print("Nothing to clean up.")
        s.enter(_CLEANUP_INTERVAL, 1, clean_up, (False,))
    else:
        print("Clean up next round.")
        s.enter(_CLEANUP_INTERVAL, 1, clean_up, (True,))


if __name__ == "__main__":
    crawl_tutti()
    s.enter(60, 1, crawl_tutti, ())
    s.enter(_CLEANUP_INTERVAL, 1, clean_up, (True,))
    s.run()

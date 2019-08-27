import json
from datetime import timedelta

import pytz
import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone

from slack.models import Check


@shared_task
def fetch():
    url = "https://waze.cryosphere.co.uk/isWazeFeedDown"
    r = requests.get(url)
    html = BeautifulSoup(r.text, 'html.parser')

    feed_status = html.find_all('blockquote')[-1].contents[0]
    print('Feed:', feed_status)
    feed_up = None
    if "down" in feed_status:
        feed_up = False
    if "up" in feed_status:
        feed_up = True

    Check.objects.create(
        feed_up=feed_up
    )
    check_send_slack_notification()


def check_send_slack_notification():
    last = Check.objects.latest('moment')
    previous = Check.objects.filter(pk__lt=last.pk).order_by('pk').last()

    if last.feed_up is None or previous.feed_up is None:
        return False

    if last.feed_up is not previous.feed_up:
        send_slack_notification(last.pk)


def send_slack_notification(check_id):
    print('Sending notification')
    url = "https://webhook.site/981097bd-aaa6-4bc8-b075-dc94081555e1"
    check = Check.objects.get(pk=check_id)
    feed_status = "UP" if check.feed_up else "DOWN"
    emoji = ":white_check_mark:" if check.feed_up else ":warning:"
    message = "%s De Waze Feed is op dit moment: *%s!*" % (emoji, feed_status)
    moment = check.moment
    headers = {'Content-Type': 'application/json'}
    timezone = pytz.timezone('Europe/Amsterdam')
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Laatst bijgewerkt: %s" % moment.astimezone(timezone).strftime('%d-%m-%Y %H:%M')
                }
            ]
        }
    ]
    data = {
        "text": message,
        "blocks": blocks
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    r.raise_for_status()


def cleanup_checks():
    before = timezone.now() - timedelta(days=2)
    checks = Check.objects.filter(moment__lte=before)
    checks.delete()

from django.core.management import BaseCommand

from slack.tasks import fetch, send_slack_notification, check_send_slack_notification, cleanup_checks


class Command(BaseCommand):
    def handle(self, *args, **options):
        cleanup_checks()

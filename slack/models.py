from django.db import models


class Check(models.Model):
    moment = models.DateTimeField(auto_now_add=True)
    feed_up = models.BooleanField(null=True)
    fetch_up = models.BooleanField(null=True)

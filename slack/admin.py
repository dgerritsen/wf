from django.contrib import admin

from slack.models import Check


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ('id', 'feed_up', 'fetch_up', 'moment')

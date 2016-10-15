from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.contrib import admin
from django.db import models


class Publication(models.Model):
    title = models.CharField(max_length=140)
    publishedAt = models.DateTimeField()

    class Meta:
        abstract = True
        ordering = ['-publishedAt']


@python_2_unicode_compatible
class AgendaItem(models.Model):
    title = models.CharField(max_length=140)
    type = models.CharField(max_length=140)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start']


@python_2_unicode_compatible
class Bulletin(Publication):
    body = models.TextField()

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class ContactItem(models.Model):
    displayName = models.CharField(max_length=140)
    email = models.CharField(max_length=500)
    order = models.IntegerField()
    detailText = models.CharField(max_length=140)

    def __str__(self):
        return self.displayName

    class Meta:
        ordering = ['order']


@python_2_unicode_compatible
class Newsletter(Publication):
    documentUrl = models.CharField(max_length=500)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class TimelineItem(Publication):
    """
    Represents all stuff we show in a time line, that is, Newsletters and Bulletins.
    """
    type = models.TextField(max_length=10)
    body = models.TextField(null=True)
    documentUrl = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.title

    class Meta:
        managed = False    # This model class has no table of its own.


class UserDevice(models.Model):
    """
    Push notification settings for a user (more accurately: for a device).

    Note: username/password pairs are random strings, apps enroll into django behind the scenes. Therefore there is no
    point in having a OneToMany from User to UserDevice; every device is a new user (also every app reset).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    wants_push_notifications = models.BooleanField(default=False)
    firebase_instance_id = models.CharField(max_length=256, null=True)

    # No need for Manufacturer, Model, etc. We track those via normal analytics, if at all.
    class Meta:
        ordering = ('-updated',)


class UserDeviceAdmin(admin.ModelAdmin):
    """
    Customizes the admin screen for UserDevice.

    By convention this should live in admin.py, but I prefer having it close to the model object.
    """
    list_display = ('user', 'wants_push_notifications', 'firebase_instance_id', 'created', 'updated')
    readonly_fields = ('firebase_instance_id',)

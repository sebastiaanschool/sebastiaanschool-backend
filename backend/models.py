from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from django.contrib import admin


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

class AgendaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'type')


@python_2_unicode_compatible
class Bulletin(Publication):
    body = models.TextField()

    def __str__(self):
        return self.title

class BulletinAdmin(admin.ModelAdmin):
    list_display = ('title', 'publishedAt')


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

class ContactItemAdmin(admin.ModelAdmin):
    list_display = ('displayName', 'email', 'order')

@python_2_unicode_compatible
class Newsletter(Publication):
    documentUrl = models.CharField(max_length=500)

    def __str__(self):
        return self.title

class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'publishedAt', 'documentUrl')


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

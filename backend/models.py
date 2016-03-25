from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models


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
class Bulletin(models.Model):
    title = models.CharField(max_length=140)
    body = models.TextField()
    publishedAt = models.DateTimeField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publishedAt']


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
class NewsLetter(models.Model):
    title = models.CharField(max_length=140)
    documentUrl = models.CharField(max_length=500)
    publishedAt = models.DateTimeField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publishedAt']

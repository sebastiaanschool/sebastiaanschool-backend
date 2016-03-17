from __future__ import unicode_literals

from django.db import models


class AgendaItem(models.Model):
    title = models.CharField(max_length=140)
    type = models.CharField(max_length=140)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return self.title


class Bulletin(models.Model):
    title = models.CharField(max_length=140)
    body = models.TextField()
    publishedAt = models.DateTimeField()

    def __str__(self):
        return self.title


class ContactItem(models.Model):
    displayName = models.CharField(max_length=140)
    email = models.CharField(max_length=500)
    order = models.IntegerField()
    detailText = models.CharField(max_length=140)

    def __str__(self):
        return self.displayName


class NewsLetter(models.Model):
    title = models.CharField(max_length=140)
    documentUrl = models.CharField(max_length=500)
    publishedAt = models.DateTimeField()

    def __str__(self):
        return self.title

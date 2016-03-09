from __future__ import unicode_literals

from django.db import models

# Create your models here.

class AgendaItem(models.Model):
    name = models.CharField(max_length = 140)
    type = models.CharField(max_length = 140)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return self.name

class Bulletin(models.Model):
    title = models.CharField(max_length = 140)
    body = models.TextField()

    def __str__(self):
        return self.title

class ContactItem(models.Model):
    displayName = models.CharField(max_length = 140)
    email = models.CharField(max_length = 500)
    order = models.IntegerField()
    detailText = models.CharField(max_length = 140)

    def __str__(self):
        return self.displayName


class NewsLetter(models.Model):
    name =  models.CharField(max_length = 140)
    url =  models.CharField(max_length = 500)
    publishedAt = models.DateTimeField()

    def __str__(self):
        return self.name

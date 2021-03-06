from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


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

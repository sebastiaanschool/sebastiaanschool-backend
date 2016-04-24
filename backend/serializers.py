from rest_framework import serializers
from backend.models import AgendaItem, Bulletin, ContactItem, Newsletter


class AgendaItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AgendaItem
        fields = ('title', 'type', 'start', 'end', 'url')


class BulletinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bulletin
        fields = ('title', 'body', 'publishedAt', 'url')


class ContactItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContactItem
        fields = ('displayName', 'email', 'order', 'detailText', 'url')


class NewsletterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Newsletter
        fields = ('title', 'documentUrl', 'publishedAt', 'url')


class TimelineSerializer(serializers.Serializer):
    type = serializers.CharField()
    title = serializers.CharField()
    body = serializers.CharField(allow_blank=True)
    documentUrl = serializers.CharField(allow_blank=True)
    publishedAt = serializers.DateTimeField()

from rest_framework import serializers
from backend.models import AgendaItem, Bulletin, ContactItem, NewsLetter


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


class NewsLetterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NewsLetter
        fields = ('title', 'documentUrl', 'publishedAt', 'url')

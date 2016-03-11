from rest_framework import serializers
from backend.models import AgendaItem, Bulletin, ContactItem, NewsLetter


class AgendaItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AgendaItem
        fields = ('name', 'type', 'start', 'end')


class BulletinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bulletin
        fields = ('title', 'body', 'publishedAt')


class ContactItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContactItem
        fields = ('displayName', 'email', 'order', 'detailText')


class NewsLetterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NewsLetter
        fields = ('name', 'url', 'publishedAt')

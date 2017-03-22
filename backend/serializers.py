from rest_framework import serializers
from backend.models import AgendaItem, Bulletin, ContactItem, Newsletter
from django.contrib.auth import get_user_model

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
    url = serializers.SerializerMethodField()
    type = serializers.CharField()
    title = serializers.CharField()
    body = serializers.CharField(allow_blank=True)
    documentUrl = serializers.CharField(allow_blank=True)
    publishedAt = serializers.DateTimeField()

    def get_url(self, obj):
        # This is a bit fragile. Any changes in urls.py aren't reflected here.
        return self.context['request'].build_absolute_uri('/api/%ss/%d/' % (obj.type, obj.pk))

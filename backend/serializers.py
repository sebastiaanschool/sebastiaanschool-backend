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
    type = serializers.CharField()
    title = serializers.CharField()
    body = serializers.CharField(allow_blank=True)
    documentUrl = serializers.CharField(allow_blank=True)
    publishedAt = serializers.DateTimeField()


class UserSerializer(serializers.ModelSerializer):
    """
    Taken from http://stackoverflow.com/a/29867704/49489 and http://stackoverflow.com/a/34428116/49489
    """
    # TODO needs work
    # TODO check if this approach yields randomized (un-enumerable) primary keys
    class Meta:
        model = get_user_model()
        fields = ('username', 'password')
        write_only_fields = ('password',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username'],
            first_name='Self-enrolled via API'
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

from datetime import datetime

from django.contrib.auth import logout, get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from push_notifications.models import APNSDevice, GCMDevice
from rest_framework import permissions
from rest_framework import views, viewsets
from rest_framework.decorators import permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from backend.models import AgendaItem, Bulletin, ContactItem, Newsletter, TimelineItem
from backend.serializers import AgendaItemSerializer, BulletinSerializer, ContactItemSerializer, NewsletterSerializer, TimelineSerializer


class AgendaItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows agenda items to be viewed or edited.
    """
    queryset = AgendaItem.objects.all()
    serializer_class = AgendaItemSerializer

    def get_queryset(self):
        if 'all' in self.request.query_params:
            selection = self.queryset
        else:
            cutoff_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            selection = self.queryset.exclude(start__lt=cutoff_date)
        return selection


class BulletinViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bulletins to be viewed or edited.

    Shows only bulletins where the publishedAt date is not in the future. Append `?all` to the request path to include
    future bulletins (admins only).
    """
    queryset = Bulletin.objects.all()
    serializer_class = BulletinSerializer

    def get_queryset(self):
        if self.request.user.is_superuser and 'all' in self.request.query_params:
            selection = self.queryset
        else:
            selection = self.queryset.exclude(publishedAt__gt=timezone.now())
        return selection


class ContactItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows contact items to be viewed or edited.
    """
    queryset = ContactItem.objects.all()
    serializer_class = ContactItemSerializer


class NewsletterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows news letters to be viewed or edited.

    Shows only bulletins where the publishedAt date is not in the future. Append `?all` to the request path to include
    future newsletters (admins only).
    """
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    def get_queryset(self):
        if self.request.user.is_superuser and 'all' in self.request.query_params:
            selection = self.queryset
        else:
            selection = self.queryset.exclude(publishedAt__gt=timezone.now())
        return selection


class TimelineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that returns newsletters and bulletins in a combined timeline.
    """
    from datetime import timedelta
    cutoff_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    queryset = TimelineItem.objects.raw(
        """
        SELECT
          id, 'bulletin' AS type, title, body, NULL AS documentUrl, publishedAt
          FROM backend_bulletin
          WHERE publishedAt < %s
        UNION SELECT
          id, 'newsletter' AS type, title AS title, NULL AS body, documentUrl, publishedAt
          FROM backend_newsletter
          WHERE publishedAt < %s
        ORDER BY
          publishedAt DESC
        """, [cutoff_date, cutoff_date])
    serializer_class = TimelineSerializer


@permission_classes((permissions.AllowAny,))
class UserEnrollmentRPC(views.APIView):
    """
    RPC endpoint for user enrollment.

    Allowed URL patterns:
    - POST     /api/enrollment   Request body: {"username": string, "password": string}
    - DELETE   /api/enrollment

    HTTPie test commands:
    $ http --json POST http://localhost:8000/api/enrollment username=zeventien-letters password=zeventien-letters
    $ http --auth zeventien-letters:zeventien-letters DELETE http://localhost:8000/api/enrollment
    """

    throttle_scope = 'enrollment'
    parser_classes = (JSONParser,)

    def post(self, request):
        if request.user.is_authenticated:
            return Response(data=None, status=400)

        username = request.data['username']
        if type(username) is not unicode:
            return self.bad_request('username should be string')
        if not 16 < len(username) <= 150:
            return self.bad_request('username should be >16 and <=150')

        password = request.data['password']
        if type(password) is not unicode:
            return self.bad_request('password should be string')
        if not 16 < len(password) <= 256:
            return self.bad_request('password should be >16 and <=256')

        if get_user_model().objects.filter(username=username).exists():
            return Response(data=None, status=409)

        group, created = Group.objects.get_or_create(name="self-enrolled")
        if created:
            group.save()
        user = get_user_model().objects.create(
            username=username,
            # Shield your eyes, the next two lines are ugly.
            first_name='Self-enrolled via API',
            last_name=datetime.utcnow().isoformat()
        )
        user.set_password(password)
        user.groups.add(group)
        user.save()
        return Response(data=None, status=204)

    @staticmethod
    def get(request):
        return Response(data=None, status=405)

    @staticmethod
    def put(request):
        return Response(data=None, status=405)

    @staticmethod
    def delete(request):
        if not request.user.is_authenticated:
            return Response(data=None, status=401)
        user = request.user
        logout(request)
        user.delete()
        return Response(data=None, status=204)

    @staticmethod
    def bad_request(reason):
        return Response(data={'detail': reason}, status=400)


@permission_classes((permissions.IsAuthenticated,))
class UserPushSettingsRPC(views.APIView):
    """
    RPC endpoint for push notification settings

    We're supporting just one device registration per user. That's because we don't have a user-visible login. Devices
    self enroll with a random UUID username and password. There's one push registration per device.

    Allowed URL patterns:
    - GET     /api/push-settings
    - POST    /api/push-settings   Request body: {"service": "gcm", "active": boolean, "registration_id": string}

    HTTPie test commands:
    $ http --auth zeventien-letters:zeventien-letters GET http://localhost:8000/api/push-settings
    $ http --json --auth zeventien-letters:zeventien-letters POST http://localhost:8000/api/push-settings \
           service=apns active:=true registration_id=zeventien-letters
    $ http --json --auth zeventien-letters:zeventien-letters POST http://localhost:8000/api/push-settings \
           service=apns active:=false
    """
    JSON_SERVICE = 'service'
    JSON_SERVICES = {'apns', 'gcm'}
    JSON_ACTIVE = 'active'
    JSON_NAME = 'name'
    JSON_REGISTRATION_ID = 'registration_id'

    parser_classes = (JSONParser,)

    # Manual validation like it's 1995. Sorry 'bout that.
    def post(self, request):
        if self.JSON_SERVICE in request.data:
            service = request.data[self.JSON_SERVICE]
            if service not in self.JSON_SERVICES:
                return self.bad_request('service should be one of [%s]' % ','.join(self.JSON_SERVICES))
        else:
            return self.bad_request('service is required')

        new_active = False
        if self.JSON_ACTIVE in request.data:
            new_active = request.data[self.JSON_ACTIVE]
            if type(new_active) is not bool:
                return self.bad_request('active should be true or false')

        new_registration_id = None
        if self.JSON_REGISTRATION_ID in request.data:
            new_registration_id = request.data[self.JSON_REGISTRATION_ID]
            if type(new_registration_id) is not unicode:
                return self.bad_request('registration_id should be string')
            if not 16 < len(new_registration_id) <= 256:
                return self.bad_request('registration_id should be >16 and <=256')

        new_name = None
        if self.JSON_NAME in request.data:
            new_name = request.data[self.JSON_NAME]
            if type(new_name) is not unicode:
                return self.bad_request('name should be string')
            if len(new_name) > 255:
                return self.bad_request('name should be <256')

        if new_active and new_registration_id is None:
            return self.bad_request('registration_id is required if active is true')

        ud = find_device_for_user(user=request.user)
        if ud is not None:
            if (service == 'gcm' and not isinstance(ud, GCMDevice)) or\
                    (service == 'apns' and not isinstance(ud, APNSDevice)):
                return self.bad_request('cannot switch from apns to gcm or vice versa')
            ud.active=new_active
            # There's a non-null constraint on registration_id, so use the old value if we have no new one
            ud.registration_id=new_registration_id if new_registration_id is not None else ud.registration_id
            ud.name=new_name if new_name is not None else ud.name
            ud.save()
        else:
            device_class = APNSDevice if service == 'apns' else GCMDevice
            ud = device_class.objects.create(user=request.user,
                                             active=new_active,
                                             name=new_name,
                                             registration_id=new_registration_id)
        return Response(data={self.JSON_ACTIVE: ud.active}, status=200)

    def get(self, request):
        push_enabled = False
        ud = find_device_for_user(user=request.user)
        if ud is not None:
            push_enabled = ud.active
        body = {self.JSON_ACTIVE: push_enabled}
        return Response(data=body, status=200)

    @staticmethod
    def put(request):
        return Response(data=None, status=405)

    @staticmethod
    def delete(request):
        return Response(data=None, status=405)

    @staticmethod
    def bad_request(reason):
        return Response(data={'detail': reason}, status=400)


def find_device_for_user(user):
    try:
        return APNSDevice.objects.get(user=user)
    except APNSDevice.DoesNotExist:
        pass
    try:
        return GCMDevice.objects.get(user=user)
    except GCMDevice.DoesNotExist:
        pass
    return None

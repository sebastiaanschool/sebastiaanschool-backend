from datetime import datetime

from django.contrib.auth import logout, get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import permissions
from rest_framework import views, viewsets
from rest_framework.decorators import permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from backend.models import AgendaItem, Bulletin, ContactItem, Newsletter, TimelineItem, UserDevice
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
        UserDevice.objects.create(user=user)
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

    Allowed URL patterns:
    - GET     /api/push-settings
    - POST    /api/push-settings   Request body: {"notify_me": boolean, "firebase_iid": string}

    HTTPie test commands:
    $ http --auth zeventien-letters:zeventien-letters GET http://localhost:8000/api/push-settings
    $ http --json --auth zeventien-letters:zeventien-letters POST http://localhost:8000/api/push-settings \
           notify_me:=true firebase_iid=zeventien-letters
    $ http --json --auth zeventien-letters:zeventien-letters POST http://localhost:8000/api/push-settings \
           notify_me:=false
    """
    JSON_NOTIFY_ME = 'notify_me'
    JSON_FIREBASE_IID = 'firebase_iid'

    parser_classes = (JSONParser,)

    # Manual validation like it's 1995. Sorry 'bout that.
    def post(self, request):
        wants_notifications = False
        if self.JSON_NOTIFY_ME in request.data:
            wants_notifications = request.data[self.JSON_NOTIFY_ME]
            if type(wants_notifications) is not bool:
                return self.bad_request('notify_me should be true or false')

        firebase_iid = None
        if self.JSON_FIREBASE_IID in request.data:
            firebase_iid = request.data[self.JSON_FIREBASE_IID]
            if type(firebase_iid) is not unicode:
                return self.bad_request('firebase_iid should be string')
            if not 16 < len(firebase_iid) <= 256:
                return self.bad_request('firebase_iid should be >16 and <=256')

        if wants_notifications and firebase_iid is None:
            return self.bad_request('firebase_iid is required if notify_me is true')

        if not wants_notifications:
            firebase_iid = None

        try:
            ud = UserDevice.objects.get(user=request.user)
            ud.wants_push_notifications=wants_notifications
            ud.firebase_instance_id=firebase_iid
            ud.save()
        except UserDevice.DoesNotExist:
            ud = UserDevice.objects.create(user=request.user,
                                           wants_push_notifications=wants_notifications,
                                           firebase_instance_id=firebase_iid)
        return Response(data={self.JSON_NOTIFY_ME: ud.wants_push_notifications}, status=200)

    def get(self, request):
        push_enabled = False
        try:
            ud = UserDevice.objects.get(user=request.user)
            push_enabled = ud.wants_push_notifications
        except UserDevice.DoesNotExist:
            pass
        body = {self.JSON_NOTIFY_ME: push_enabled}
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

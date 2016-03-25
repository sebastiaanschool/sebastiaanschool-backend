from django.utils import timezone
from rest_framework import viewsets

from backend.models import AgendaItem, Bulletin, ContactItem, NewsLetter, TimelineItem
from backend.serializers import AgendaItemSerializer, BulletinSerializer, ContactItemSerializer, NewsLetterSerializer, TimelineSerializer


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


class NewsLetterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows news letters to be viewed or edited.

    Shows only bulletins where the publishedAt date is not in the future. Append `?all` to the request path to include
    future newsletters (admins only).
    """
    queryset = NewsLetter.objects.all()
    serializer_class = NewsLetterSerializer

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
    cutoff_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    queryset = TimelineItem.objects.raw(
        """
        SELECT
          id, 'bulletin' AS type, title, body, NULL AS documentUrl, publishedAt
          FROM backend_bulletin
          WHERE publishedAt >= %s
        UNION SELECT
          id, 'newsletter' AS type, title AS title, NULL AS body, documentUrl, publishedAt
          FROM backend_newsletter
          WHERE publishedAt >= %s
        ORDER BY
          publishedAt DESC
        """, [cutoff_date, cutoff_date])
    serializer_class = TimelineSerializer

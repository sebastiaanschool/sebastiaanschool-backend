from datetime import date

from backend.models import AgendaItem, Bulletin, ContactItem, NewsLetter
from rest_framework import viewsets
from backend.serializers import AgendaItemSerializer, BulletinSerializer, ContactItemSerializer, NewsLetterSerializer


class AgendaItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows agenda items to be viewed or edited.
    """
    queryset = AgendaItem.objects.all().order_by('-start')
    serializer_class = AgendaItemSerializer


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
        selection = self.queryset.order_by('-publishedAt')
      else:
        selection = self.queryset.exclude(publishedAt__gt=date.today()).order_by('-publishedAt')
      return selection


class ContactItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows contact items to be viewed or edited.
    """
    queryset = ContactItem.objects.order_by('order').all()
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
        selection = self.queryset.order_by('-publishedAt')
      else:
        selection = self.queryset.exclude(publishedAt__gt=date.today()).order_by('-publishedAt')
      return selection

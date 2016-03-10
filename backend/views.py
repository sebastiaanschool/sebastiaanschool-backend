from django.shortcuts import render
from datetime import date

from rest_framework.decorators import list_route
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from backend.models import AgendaItem, Bulletin, ContactItem, NewsLetter
from rest_framework import viewsets
from backend.serializers import AgendaItemSerializer, BulletinSerializer, ContactItemSerializer, NewsLetterSerializer

# Create your views here.
class AgendaItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows agenda items to be viewed or edited.
    """
    queryset = AgendaItem.objects.all().order_by('-start')
    serializer_class = AgendaItemSerializer


class BulletinViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bulletins to be viewed or edited.

    Shows only bulletins where the publishedAt date is not in the future. Append `/all/` to the request path to include
    future bulletins (admins only).
    """
    queryset = Bulletin.objects.exclude(publishedAt__gt=date.today()).order_by('-publishedAt')
    serializer_class = BulletinSerializer

    @list_route(permission_classes=[IsAdminUser])
    def all(self, request):
        selection = Bulletin.objects.all().order_by('-publishedAt')
        serializer = self.get_serializer(selection, many=True)
        return Response(serializer.data)


class ContactItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows contact items to be viewed or edited.
    """
    queryset = ContactItem.objects.all()
    serializer_class = ContactItemSerializer

class NewsLetterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows news letters to be viewed or edited.

    Shows only bulletins where the publishedAt date is not in the future. Append `/all/` to the request path to include
    future newsletters (admins only).
    """
    queryset = NewsLetter.objects.exclude(publishedAt__gt=date.today()).order_by('-publishedAt')
    serializer_class = NewsLetterSerializer

    @list_route(permission_classes=[IsAdminUser])
    def all(self, request):
        selection = NewsLetter.objects.all().order_by('-publishedAt')
        serializer = self.get_serializer(selection, many=True)
        return Response(serializer.data)

from django.shortcuts import render
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
    """
    queryset = Bulletin.objects.all().order_by('-publishedAt')
    serializer_class = BulletinSerializer

class ContactItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows contact items to be viewed or edited.
    """
    queryset = ContactItem.objects.all()
    serializer_class = ContactItemSerializer

class NewsLetterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows news letters to be viewed or edited.
    """
    queryset = NewsLetter.objects.all()
    serializer_class = NewsLetterSerializer

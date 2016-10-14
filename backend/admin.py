from django.contrib import admin
from backend.models import AgendaItem, Bulletin, ContactItem, Newsletter, UserDevice

# Register your models here.
admin.site.register(AgendaItem)
admin.site.register(Bulletin)
admin.site.register(ContactItem)
admin.site.register(Newsletter)
admin.site.register(UserDevice)

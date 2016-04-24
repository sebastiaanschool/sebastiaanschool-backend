from django.contrib import admin
from backend.models import AgendaItem, AgendaItemAdmin
from backend.models import Bulletin, BulletinAdmin
from backend.models import ContactItem, ContactItemAdmin
from backend.models import Newsletter, NewsletterAdmin

# Register your models here.
admin.site.register(AgendaItem, AgendaItemAdmin)
admin.site.register(Bulletin, BulletinAdmin)
admin.site.register(ContactItem, ContactItemAdmin)
admin.site.register(Newsletter, NewsletterAdmin)

from django.contrib import admin
from .models import Event, Venue, Visitor

admin.site.register(Event)
admin.site.register(Venue)
admin.site.register(Visitor)
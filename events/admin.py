from django.contrib import admin
from .models import Event, Visitor, Requisition

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image')
    search_fields = ('name', 'description')


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('fname', 'mobile', 'created_at')
    search_fields = ('fname', 'mobile')
    readonly_fields = ('created_at',)


@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('visitor_name', 'event', 'phone', 'email', 'number_of_people', 'venue_type', 'budget')
    search_fields = ('visitor_name', 'event__name', 'phone', 'email', 'venue_type')
    list_filter = ('event', 'venue_type', 'religious_affiliation')
    readonly_fields = ('created_at',)

from django.contrib import admin
from .models import Event, Visitor, Requisition, ExtraRequisitions, VenueType, VenueRequisition

# ---------------- EVENTS ----------------
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'image')
    search_fields = ('name', 'description')
    ordering = ('-id',)


# ---------------- VISITORS ----------------
@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'fname', 'mobile', 'created_at')
    search_fields = ('fname', 'mobile')
    ordering = ('-created_at',)


# ---------------- VENUE INVENTORY INLINE ----------------
class VenueRequisitionInline(admin.TabularInline):
    model = VenueRequisition
    extra = 1


# ---------------- VENUES ----------------
@admin.register(VenueType)
class VenueTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'area', 'old_price', 'discounted_price', 'created_at')
    search_fields = ('name', 'location', 'area', 'city', 'venue_type')
    ordering = ('-id',)
    inlines = [VenueRequisitionInline]


# ---------------- EXTRA REQUISITIONS INLINE ----------------
class ExtraRequisitionsInline(admin.StackedInline):
    model = ExtraRequisitions
    can_delete = False
    verbose_name_plural = 'Extra Requisitions'
    fk_name = 'requisition'
    readonly_fields = ('created_at', 'updated_at', 'total_cost')


# ---------------- REQUISITIONS ----------------
@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'event', 'visitor_name', 'phone', 'email',
        'number_of_people', 'venue_type', 'budget', 'created_at'
    )
    search_fields = ('visitor_name', 'phone', 'email', 'venue_type', 'event__name')
    inlines = (ExtraRequisitionsInline,)
    ordering = ('-created_at',)


# ---------------- VENUE INVENTORY ----------------
@admin.register(VenueRequisition)
class VenueRequisitionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'venue',
        'tables_count',
        'chairs_count',
        'baloons_count',
        'garlands_count',
        'decor_type',
        'band_type',
        'DJ_type',
    )
    search_fields = ('venue__name',)
    ordering = ('venue',)
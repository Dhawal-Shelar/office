from django.contrib import admin
from django.urls import path
from events import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home / Events
    path('', views.events_home, name='events_home'),

    # Visitor popup
    path('visitor-popup-submit/', views.visitor_popup_submit, name='visitor_popup_submit'),

    # Event information & requisition
    path('information/<int:event_id>/', views.information_view, name='information_view'),

    # Venues listing (shows VenueType + VenueRequisition inventory)
    path('venues/', views.venue_view, name='venue_view'),

    # AJAX: Save selected venue
    path('save-selected-venue/', views.save_selected_venue, name='save_selected_venue'),

    # Extra Requisitions
    path('extra-requisitions/<int:requisition_id>/', views.extra_requisitions_view, name='extra_requisitions_view'),

    # Requisitions list (password protected)
    path('requisitions/', views.requisitions_list, name='requisitions_list'),

    # Static pages
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('contact/', views.contact_view, name='contact'),

    # Optional: dedicated view for venue inventories (can show available venues)
    path('venue-inventory/', views.venue_view, name='venue_inventory_view'),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

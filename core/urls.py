from django.contrib import admin
from django.urls import path,include
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

    # Visitor requisitions
    path('visitor_requisition/', views.visitor_requisition, name='visitor_requisition'),

    # Event information & requisition
    path('information/<int:event_id>/', views.information_view, name='information_view'),

    # Venues listing
    path('venues/', views.venue_view, name='venue_view'),

    # AJAX: Save selected venue
    path('save-selected-venue/', views.save_selected_venue, name='save_selected_venue'),

    # Extra Requisitions
    path('extra_requisitions/<int:requisition_id>/', views.extra_requisitions_view, name='extra_requisitions'),
    path('save_extra_requisition/', views.save_extra_requisition, name='save_extra_requisition'),

    # Admin / all requisitions list (password protected)
    path('requisitions/', views.requisitions_list, name='requisitions_list'),

    # Static pages
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('contact/', views.contact_view, name='contact'),

    # Optional: dedicated view for venue inventories
    path('venue-inventory/', views.venue_view, name='venue_inventory_view'),

    # Payment page for logged-in visitor
    path('payment/', views.payment_page, name='payment_page'),
    
    
    path("accounts/", include("allauth.urls")),  # allauth URLs

]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

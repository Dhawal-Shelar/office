from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path('', views.events_home, name='events_home'),
    path('visitor-popup-submit/', views.visitor_popup_submit, name='visitor_popup_submit'),
    path('visitor-requisition/', views.visitor_requisition, name='visitor_requisition'),
    path('information/<int:event_id>/', views.information_view, name='information_view'),
    path('venues/', views.venue_view, name='venue_view'),
    path('save_selected_venue/', views.save_selected_venue, name='save_selected_venue'),
    path('extra_requisitions/<int:requisition_id>/', views.extra_requisitions_view, name='extra_requisitions'),
    path('save_extra_requisition/', views.save_extra_requisition, name='save_extra_requisition'),
    path('requisitions/', views.requisitions_list, name='requisitions_list'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('contact/', views.contact_view, name='contact'),
    path('payment/', views.payment_page, name='payment_page'),
]

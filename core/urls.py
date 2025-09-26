from django.contrib import admin
from django.urls import path
from events import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.events_home, name='events_home'),
    path('visitor-popup-submit/', views.visitor_popup_submit, name='visitor_popup_submit'),
    path('information/<int:event_id>/', views.information_view, name='information_view'),
    path('requisitions/', views.requisitions_list, name='requisitions_list'),    
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('contact/', views.contact_view, name='contact'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

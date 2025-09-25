from django.contrib import admin
from django.urls import path
from events import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.events_home, name='events_home'),
    path('visitor_login/<int:event_id>/', views.visitor_login, name='visitor_login'),
    path('venue/<int:event_id>/', views.venue_view, name='venue_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

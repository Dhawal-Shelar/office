from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),

    # Delegate everything related to events app
    path('', lambda request: redirect('events:events_home')),  # root redirect to /events/
    path('events/', include("events.urls", namespace="events")),

    # Allauth for login/signup
    path("accounts/", include("allauth.urls")),
]

# Media + static in dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

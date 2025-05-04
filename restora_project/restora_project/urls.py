from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

# Importing the index view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.accounts_bridge_core.urls')),
    path('api/', include('api.notifications_bridge_core.urls')),
    path('api/', include('menu_bridge_core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
 
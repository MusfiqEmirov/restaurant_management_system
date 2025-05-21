from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),  # /restaurant/admin/

    # Main API
    path('api/v1/accounts/', include('api.accounts_bridge_core.urls')),
    path('api/v1/notifications/', include('api.notifications_bridge_core.urls')),
    path('api/v1/menu/', include('api.menu_bridge_core.urls')),
    path('api/v1/orders/', include('api.orders_bridge_core.urls')),
    path('api/v1/staff/', include('api.staff_bridge_core.urls')),
    path('api/v1/customers/', include('api.customers_bridge_core.urls')),

    # API Schema and Documentation
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Static and media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

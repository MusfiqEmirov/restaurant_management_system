from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import api_urls

urlpatterns = [
    path('restaurant/admin/', admin.site.urls),
    path('restaurant/api/v1/', include(api_urls)),
    path('restaurant/api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('restaurant/api/v1/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('restaurant/api/v1/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('accounts/', include('api.accounts_bridge_core.urls')),
    path('notifications/', include('api.notifications_bridge_core.urls')),
    path('menu/', include('api.menu_bridge_core.urls')),
    path('orders/', include('api.orders_bridge_core.urls')),
    path('staff/', include('api.staff_bridge_core.urls')),
    path('customers/', include('api.customers_bridge_core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

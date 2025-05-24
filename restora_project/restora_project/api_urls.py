from django.urls import path, include

urlpatterns = [
    path('accounts/', include('api.accounts_bridge_core.urls')),
    path('notifications/', include('api.notifications_bridge_core.urls')),
    path('menu/', include('api.menu_bridge_core.urls')),
    path('orders/', include('api.orders_bridge_core.urls')),
    path('staff/', include('api.staff_bridge_core.urls')),
    path('customers/', include('api.customers_bridge_core.urls')),
]
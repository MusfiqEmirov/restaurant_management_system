from django.urls import path
from .views import (OrderView,
                    OrderItemView,
                    SalesReportView
                    )

urlpatterns = [
    path('orders/', OrderView.as_view(), name='order_list'),
    path('orders/<int:order_id>/', OrderView.as_view(), name='order_detail'),
    path('order-items/', OrderItemView.as_view(), name='order_item_list'),
    path('order-items/<int:item_id>/', OrderItemView.as_view(), name='order_item_detail'),
    path('orders/report/', SalesReportView.as_view(), name='sales_report'),
]
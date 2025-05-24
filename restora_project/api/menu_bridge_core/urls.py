from django.urls import path
from .views import CategoryView, MenuItemView

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='category_list'),
    path('categories/<int:category_id>/', CategoryView.as_view(), name='category_detail'),
    path('items/', MenuItemView.as_view(), name='menu_item_list'),
    path('items/<int:item_id>/', MenuItemView.as_view(), name='menu_item_detail'),
]
from django.urls import path
from .views import CategoryView, MenuItemView

urlpatterns = [
    path('menu/categories/', CategoryView.as_view(), name='category_list'),
    path('menu/categories/<int:category_id>/', CategoryView.as_view(), name='category_detail'),
    path('menu/items/', MenuItemView.as_view(), name='menu_item_list'),
    path('menu/items/<int:item_id>/', MenuItemView.as_view(), name='menu_item_detail'),
]
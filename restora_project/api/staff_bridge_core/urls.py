from django.urls import path
from .views import StaffView

urlpatterns = [
    path('', StaffView.as_view(), name='staff_list'),
    path('<int:staff_id>/', StaffView.as_view(), name='staff_detail'),
]
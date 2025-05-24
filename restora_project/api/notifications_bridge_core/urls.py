from django.urls import path
from .views import MessageCreateView

urlpatterns = [
    path('messages/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:message_id>/', MessageCreateView.as_view(), name='message_detail'),
]
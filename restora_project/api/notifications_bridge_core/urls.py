from django.urls import path
from .views import MessageCreateView

urlpatterns = [
    path('notifications/messages/', MessageCreateView.as_view(), name='message_create'),
]
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from project_apps.notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationsViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Create notifications
        self.notification1 = Notification.objects.create(
            user=self.user,
            title='Test Notification 1',
            message='This is a test notification 1',
            notification_type='order_status',
            is_read=False
        )

        self.notification2 = Notification.objects.create(
            user=self.user,
            title='Test Notification 2',
            message='This is a test notification 2',
            notification_type='system',
            is_read=True
        )

    def test_notification_list(self):
        url = reverse('api:notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_notification_create(self):
        url = reverse('api:notification-list')
        data = {
            'title': 'New Notification',
            'message': 'This is a new notification',
            'notification_type': 'system'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 3)

    def test_notification_detail(self):
        url = reverse('api:notification-detail', args=[self.notification1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Notification 1')
        self.assertEqual(response.data['is_read'], False)

    def test_notification_mark_as_read(self):
        url = reverse('api:notification-mark-read', args=[self.notification1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_notification = Notification.objects.get(id=self.notification1.id)
        self.assertTrue(updated_notification.is_read)

    def test_notification_mark_all_as_read(self):
        url = reverse('api:notification-mark-all-read')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unread_notifications = Notification.objects.filter(is_read=False)
        self.assertEqual(unread_notifications.count(), 0)

    def test_notification_delete(self):
        url = reverse('api:notification-detail', args=[self.notification1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.count(), 1)

    def test_notification_filter_by_type(self):
        url = reverse('api:notification-list')
        response = self.client.get(url, {'notification_type': 'order_status'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['notification_type'], 'order_status')

    def test_notification_filter_by_read_status(self):
        url = reverse('api:notification-list')
        response = self.client.get(url, {'is_read': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['is_read'], False) 
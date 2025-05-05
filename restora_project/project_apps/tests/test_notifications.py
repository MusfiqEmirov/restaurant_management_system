from django.test import TestCase
from project_apps.notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationModelTest(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='notificationuser',
            email='notification@example.com',
            password='testpass123'
        )

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

    def test_notification_creation(self):
        self.assertEqual(self.notification1.user, self.user)
        self.assertEqual(self.notification1.title, 'Test Notification 1')
        self.assertEqual(self.notification1.message, 'This is a test notification 1')
        self.assertEqual(self.notification1.notification_type, 'order_status')
        self.assertFalse(self.notification1.is_read)

    def test_notification_str_method(self):
        self.assertEqual(str(self.notification1), f'Notification: {self.notification1.title}')

    def test_notification_mark_as_read(self):
        self.notification1.mark_as_read()
        self.assertTrue(self.notification1.is_read)

    def test_notification_mark_as_unread(self):
        self.notification2.mark_as_unread()
        self.assertFalse(self.notification2.is_read)

    def test_notification_filtering(self):
        unread_notifications = Notification.objects.filter(user=self.user, is_read=False)
        self.assertEqual(unread_notifications.count(), 1)
        self.assertEqual(unread_notifications.first(), self.notification1)

        read_notifications = Notification.objects.filter(user=self.user, is_read=True)
        self.assertEqual(read_notifications.count(), 1)
        self.assertEqual(read_notifications.first(), self.notification2)

    def test_notification_type_filtering(self):
        order_notifications = Notification.objects.filter(notification_type='order_status')
        self.assertEqual(order_notifications.count(), 1)
        self.assertEqual(order_notifications.first(), self.notification1)

        system_notifications = Notification.objects.filter(notification_type='system')
        self.assertEqual(system_notifications.count(), 1)
        self.assertEqual(system_notifications.first(), self.notification2) 
from django.test import TestCase
from django.contrib.auth import get_user_model
from project_apps.accounts.models import UserProfile

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            phone_number='1234567890',
            address='Test Address'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_profile_creation(self):
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user_profile.phone_number, '1234567890')
        self.assertEqual(self.user_profile.address, 'Test Address')

    def test_user_str_method(self):
        self.assertEqual(str(self.user), 'testuser')

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone_number='9876543210',
            address='Profile Address'
        )

    def test_profile_str_method(self):
        self.assertEqual(str(self.profile), f'Profile of {self.user.username}')

    def test_profile_update(self):
        self.profile.phone_number = '5555555555'
        self.profile.save()
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.phone_number, '5555555555') 
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import Profile


class UserModelTest(TestCase):
    def test_create_user(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword",
            email="testuser@example.com",
            phone_number="123456789"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.check_password("testpassword"))
        self.assertEqual(user.phone_number, "123456789")

    def test_create_user_with_role(self):
        user = get_user_model().objects.create_user(
            username="customeruser",
            password="testpassword",
            email="customeruser@example.com",
            role="customer"
        )
        self.assertEqual(user.role, "customer")


class ProfileModelTest(TestCase):
    def test_create_profile(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword",
            email="testuser@example.com"
        )
        profile = Profile.objects.create(
            user=user,
            address="123 Test Street",
            loyalty_points=100
        )
        self.assertEqual(profile.user.username, "testuser")
        self.assertEqual(profile.address, "123 Test Street")
        self.assertEqual(profile.loyalty_points, 100)

    def test_profile_str_method(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword",
            email="testuser@example.com"
        )
        profile = Profile.objects.create(
            user=user,
            address="123 Test Street",
            loyalty_points=100
        )
        self.assertEqual(str(profile), "testuser profili")

    def test_profile_with_no_loyalty_points(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword",
            email="testuser@example.com"
        )
        profile = Profile.objects.create(user=user)
        self.assertEqual(profile.loyalty_points, 0)

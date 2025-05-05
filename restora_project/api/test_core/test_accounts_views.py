from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from project_apps.accounts.models import UserProfile

User = get_user_model()

class AccountsViewsTest(TestCase):
    """
    Test cases for Account related API endpoints.
    
    This test suite covers:
    - User registration
    - User login
    - Profile management
    - Logout functionality
    """

    def setUp(self):
        self.client = APIClient()
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
        self.client.force_authenticate(user=self.user)

    def test_user_registration(self):
        """
        Test user registration endpoint.
        
        Endpoint: POST /api/register/
        Expected: Creates new user and profile
        """
        url = reverse('api:register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'phone_number': '9876543210',
            'address': 'New Address'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(UserProfile.objects.count(), 2)

    def test_user_login(self):
        """
        Test user login endpoint.
        
        Endpoint: POST /api/login/
        Expected: Returns authentication token
        """
        url = reverse('api:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_user_profile_retrieve(self):
        """
        Test user profile retrieval endpoint.
        
        Endpoint: GET /api/profile/
        Expected: Returns user profile data
        """
        url = reverse('api:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_user_profile_update(self):
        """
        Test user profile update endpoint.
        
        Endpoint: PATCH /api/profile/
        Expected: Updates user profile data
        """
        url = reverse('api:profile')
        data = {
            'phone_number': '5555555555',
            'address': 'Updated Address'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '5555555555')
        self.assertEqual(response.data['address'], 'Updated Address')

    def test_user_logout(self):
        """
        Test user logout endpoint.
        
        Endpoint: POST /api/logout/
        Expected: Logs out user and invalidates token
        """
        url = reverse('api:logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
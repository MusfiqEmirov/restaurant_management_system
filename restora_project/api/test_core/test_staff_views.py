from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from project_apps.staff.models import Staff, StaffRole
from django.contrib.auth import get_user_model

User = get_user_model()

class StaffViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create staff role
        self.role = StaffRole.objects.create(
            name='Waiter',
            description='Serves customers and takes orders'
        )

        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123'
        )
        self.staff = Staff.objects.create(
            user=self.staff_user,
            role=self.role,
            phone_number='1234567890',
            address='Staff Address',
            hire_date='2024-01-01',
            is_active=True
        )

    def test_staff_role_list(self):
        url = reverse('api:staffrole-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_staff_role_create(self):
        url = reverse('api:staffrole-list')
        data = {
            'name': 'Chef',
            'description': 'Prepares food'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StaffRole.objects.count(), 2)

    def test_staff_role_detail(self):
        url = reverse('api:staffrole-detail', args=[self.role.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Waiter')

    def test_staff_list(self):
        url = reverse('api:staff-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_staff_create(self):
        url = reverse('api:staff-list')
        data = {
            'user': {
                'username': 'newstaff',
                'email': 'newstaff@example.com',
                'password': 'newpass123'
            },
            'role': self.role.id,
            'phone_number': '9876543210',
            'address': 'New Staff Address',
            'hire_date': '2024-02-01',
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Staff.objects.count(), 2)

    def test_staff_detail(self):
        url = reverse('api:staff-detail', args=[self.staff.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'staffuser')

    def test_staff_update(self):
        url = reverse('api:staff-detail', args=[self.staff.id])
        data = {
            'phone_number': '5555555555',
            'is_active': False
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '5555555555')
        self.assertEqual(response.data['is_active'], False)

    def test_staff_delete(self):
        url = reverse('api:staff-detail', args=[self.staff.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Staff.objects.count(), 0) 
from django.test import TestCase
from project_apps.staff.models import Staff, StaffRole
from django.contrib.auth import get_user_model

User = get_user_model()

class StaffModelTest(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123'
        )

        # Create staff role
        self.role = StaffRole.objects.create(
            name='Waiter',
            description='Serves customers and takes orders'
        )

        # Create staff member
        self.staff = Staff.objects.create(
            user=self.user,
            role=self.role,
            phone_number='1234567890',
            address='Staff Address',
            hire_date='2024-01-01',
            is_active=True
        )

    def test_staff_creation(self):
        self.assertEqual(self.staff.user, self.user)
        self.assertEqual(self.staff.role, self.role)
        self.assertEqual(self.staff.phone_number, '1234567890')
        self.assertEqual(self.staff.address, 'Staff Address')
        self.assertEqual(str(self.staff.hire_date), '2024-01-01')
        self.assertTrue(self.staff.is_active)

    def test_staff_str_method(self):
        self.assertEqual(str(self.staff), f'{self.user.username} - {self.role.name}')

    def test_staff_role_creation(self):
        self.assertEqual(self.role.name, 'Waiter')
        self.assertEqual(self.role.description, 'Serves customers and takes orders')

    def test_staff_role_str_method(self):
        self.assertEqual(str(self.role), 'Waiter')

    def test_staff_update(self):
        self.staff.is_active = False
        self.staff.save()
        updated_staff = Staff.objects.get(user=self.user)
        self.assertFalse(updated_staff.is_active)

    def test_staff_role_update(self):
        self.role.name = 'Senior Waiter'
        self.role.save()
        updated_role = StaffRole.objects.get(id=self.role.id)
        self.assertEqual(updated_role.name, 'Senior Waiter') 
from django.test import TestCase
from project_apps.customers.models import Customer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='customeruser',
            email='customer@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='1234567890',
            address='Customer Address',
            loyalty_points=100
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.user, self.user)
        self.assertEqual(self.customer.phone_number, '1234567890')
        self.assertEqual(self.customer.address, 'Customer Address')
        self.assertEqual(self.customer.loyalty_points, 100)

    def test_customer_str_method(self):
        self.assertEqual(str(self.customer), f'Customer: {self.user.username}')

    def test_customer_update(self):
        self.customer.loyalty_points = 150
        self.customer.save()
        updated_customer = Customer.objects.get(user=self.user)
        self.assertEqual(updated_customer.loyalty_points, 150)

    def test_customer_loyalty_points(self):
        # Test adding loyalty points
        self.customer.add_loyalty_points(50)
        self.assertEqual(self.customer.loyalty_points, 150)

        # Test using loyalty points
        self.customer.use_loyalty_points(30)
        self.assertEqual(self.customer.loyalty_points, 120) 
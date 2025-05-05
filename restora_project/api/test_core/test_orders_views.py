from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from project_apps.orders.models import Order, OrderItem
from project_apps.menu.models import Category, MenuItem
from project_apps.customers.models import Customer
from django.contrib.auth import get_user_model

User = get_user_model()

class OrdersViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create user and customer
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='1234567890',
            address='Test Address'
        )
        self.client.force_authenticate(user=self.user)

        # Create menu items
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.menu_item1 = MenuItem.objects.create(
            name='Item 1',
            description='Description 1',
            price=10.99,
            category=self.category
        )
        self.menu_item2 = MenuItem.objects.create(
            name='Item 2',
            description='Description 2',
            price=15.99,
            category=self.category
        )

        # Create order
        self.order = Order.objects.create(
            customer=self.customer,
            total_amount=26.98,
            status='pending'
        )

        # Create order items
        self.order_item1 = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item1,
            quantity=1,
            price=10.99
        )
        self.order_item2 = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item2,
            quantity=1,
            price=15.99
        )

    def test_order_list(self):
        url = reverse('api:order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_order_create(self):
        url = reverse('api:order-list')
        data = {
            'items': [
                {
                    'menu_item': self.menu_item1.id,
                    'quantity': 2
                },
                {
                    'menu_item': self.menu_item2.id,
                    'quantity': 1
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)

    def test_order_detail(self):
        url = reverse('api:order-detail', args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(len(response.data['items']), 2)

    def test_order_update_status(self):
        url = reverse('api:order-detail', args=[self.order.id])
        data = {'status': 'completed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

    def test_order_cancel(self):
        url = reverse('api:order-cancel', args=[self.order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_order = Order.objects.get(id=self.order.id)
        self.assertEqual(updated_order.status, 'cancelled')

    def test_order_items_list(self):
        url = reverse('api:orderitem-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_order_item_detail(self):
        url = reverse('api:orderitem-detail', args=[self.order_item1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 1)
        self.assertEqual(response.data['price'], '10.99') 
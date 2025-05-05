from django.test import TestCase
from project_apps.orders.models import Order, OrderItem
from project_apps.menu.models import Category, MenuItem
from project_apps.customers.models import Customer
from django.contrib.auth import get_user_model

User = get_user_model()

class OrderModelTest(TestCase):
    def setUp(self):
        # Create user and customer
        self.user = User.objects.create_user(
            username='orderuser',
            email='order@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='1234567890',
            address='Order Address'
        )

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

    def test_order_creation(self):
        self.assertEqual(self.order.customer, self.customer)
        self.assertEqual(self.order.total_amount, 26.98)
        self.assertEqual(self.order.status, 'pending')

    def test_order_str_method(self):
        self.assertEqual(str(self.order), f'Order #{self.order.id} - {self.customer.user.username}')

    def test_order_item_creation(self):
        self.assertEqual(self.order_item1.menu_item, self.menu_item1)
        self.assertEqual(self.order_item1.quantity, 1)
        self.assertEqual(self.order_item1.price, 10.99)

    def test_order_item_str_method(self):
        self.assertEqual(str(self.order_item1), f'{self.menu_item1.name} x {self.order_item1.quantity}')

    def test_order_status_update(self):
        self.order.status = 'completed'
        self.order.save()
        updated_order = Order.objects.get(id=self.order.id)
        self.assertEqual(updated_order.status, 'completed')

    def test_order_total_calculation(self):
        total = sum(item.price * item.quantity for item in self.order.items.all())
        self.assertEqual(total, 26.98) 
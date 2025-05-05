from django.test import TestCase
from project_apps.menu.models import Category, MenuItem

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.description, 'Test Description')

    def test_category_str_method(self):
        self.assertEqual(str(self.category), 'Test Category')

class MenuItemModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.menu_item = MenuItem.objects.create(
            name='Test Item',
            description='Test Item Description',
            price=10.99,
            category=self.category,
            is_available=True
        )

    def test_menu_item_creation(self):
        self.assertEqual(self.menu_item.name, 'Test Item')
        self.assertEqual(self.menu_item.description, 'Test Item Description')
        self.assertEqual(self.menu_item.price, 10.99)
        self.assertEqual(self.menu_item.category, self.category)
        self.assertTrue(self.menu_item.is_available)

    def test_menu_item_str_method(self):
        self.assertEqual(str(self.menu_item), 'Test Item')

    def test_menu_item_update(self):
        self.menu_item.price = 15.99
        self.menu_item.save()
        updated_item = MenuItem.objects.get(id=self.menu_item.id)
        self.assertEqual(updated_item.price, 15.99) 
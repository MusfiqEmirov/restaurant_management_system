from django.test import TestCase
from project_apps.menu.models import Category, MenuItem


class MenuItemTestCase(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Drinks", description="Various types of drinks")

        self.menu_item_no_discount = MenuItem.objects.create(
            category=self.category,
            name="Lemonade",
            description="Freshly squeezed lemonade",
            price=5.00,
            is_available=True,
            discount_percentage=0
        )
        self.menu_item_with_discount = MenuItem.objects.create(
            category=self.category,
            name="Iced Tea",
            description="Refreshing iced tea",
            price=6.00,
            is_available=True,
            discount_percentage=20
        )

    def test_menu_item_creation(self):
        self.assertEqual(self.menu_item_no_discount.name, "Lemonade")
        self.assertEqual(self.menu_item_with_discount.name, "Iced Tea")
        self.assertEqual(self.menu_item_no_discount.category.name, "Drinks")
        self.assertEqual(self.menu_item_with_discount.category.name, "Drinks")

    def test_discounted_price(self):
        self.assertAlmostEqual(self.menu_item_no_discount.get_discounted_price(), 5.00)  
        self.assertAlmostEqual(self.menu_item_with_discount.get_discounted_price(), 4.80)  

    def test_no_discount(self):
        self.assertAlmostEqual(self.menu_item_no_discount.get_discounted_price(), 5.00) 

    def test_discount(self):
        self.assertAlmostEqual(self.menu_item_with_discount.get_discounted_price(), 4.80) 
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from project_apps.menu.models import Category, MenuItem
from django.contrib.auth import get_user_model

User = get_user_model()

class MenuViewsTest(TestCase):
    """
    Test cases for Menu related API endpoints.
    
    This test suite covers:
    - Category CRUD operations
    - Menu item CRUD operations
    - Menu item availability management
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        
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

    def test_category_list(self):
        """
        Test category list endpoint.
        
        Endpoint: GET /api/categories/
        Expected: Returns list of all categories
        """
        url = reverse('api:category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_category_create(self):
        """
        Test category creation endpoint.
        
        Endpoint: POST /api/categories/
        Expected: Creates new category
        """
        url = reverse('api:category-list')
        data = {
            'name': 'New Category',
            'description': 'New Description'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

    def test_category_detail(self):
        """
        Test category detail endpoint.
        
        Endpoint: GET /api/categories/{id}/
        Expected: Returns specific category details
        """
        url = reverse('api:category-detail', args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Category')

    def test_menu_item_list(self):
        """
        Test menu item list endpoint.
        
        Endpoint: GET /api/menu-items/
        Expected: Returns list of all menu items
        """
        url = reverse('api:menuitem-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_menu_item_create(self):
        """
        Test menu item creation endpoint.
        
        Endpoint: POST /api/menu-items/
        Expected: Creates new menu item
        """
        url = reverse('api:menuitem-list')
        data = {
            'name': 'New Item',
            'description': 'New Item Description',
            'price': 15.99,
            'category': self.category.id,
            'is_available': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuItem.objects.count(), 2)

    def test_menu_item_detail(self):
        """
        Test menu item detail endpoint.
        
        Endpoint: GET /api/menu-items/{id}/
        Expected: Returns specific menu item details
        """
        url = reverse('api:menuitem-detail', args=[self.menu_item.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Item')

    def test_menu_item_update(self):
        """
        Test menu item update endpoint.
        
        Endpoint: PATCH /api/menu-items/{id}/
        Expected: Updates specific menu item
        """
        url = reverse('api:menuitem-detail', args=[self.menu_item.id])
        data = {
            'price': 12.99,
            'is_available': False
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], '12.99')
        self.assertEqual(response.data['is_available'], False)

    def test_menu_item_delete(self):
        """
        Test menu item deletion endpoint.
        
        Endpoint: DELETE /api/menu-items/{id}/
        Expected: Deletes specific menu item
        """
        url = reverse('api:menuitem-detail', args=[self.menu_item.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MenuItem.objects.count(), 0) 
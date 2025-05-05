from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from project_apps.menu.models import (Category,
                                      MenuItem
                                      )
from project_apps.menu.serializers import (CategorySerializer,
                                           MenuItemSerializer
                                           )
from project_apps.core.logging import get_logger

logger = get_logger(__name__)

class CategoryView(APIView):
    def get(self, request, category_id=None):
        """
        Returns the categories and the list.
        Everyone can access, no permission required.
        """
        logger.debug(f"Category query received: {request.user.email if request.user.is_authenticated else 'Guest'}, ID: {category_id}")
        try:
            if category_id:
                category = Category.objects.filter(id=category_id, is_deleted=False).first()
                if not category:
                    logger.error(f"Category not found: ID {category_id}")
                    return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
                serializer = CategorySerializer(category)
                logger.info(f"Category details found: ID {category_id}")
                return Response(serializer.data, status=status.HTTP_200_OK)

            categories = Category.objects.filter(is_deleted=False)
            serializer = CategorySerializer(categories, many=True)
            logger.info(f"Category list returned: count: {categories.count()}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error while retrieving category list: {str(e)}", exc_info=True)
            return Response({'error': 'Error while retrieving category list'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        Create a new category, only for admins.
        """
        logger.debug(f"Category creation query received: {request.data}")
        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"Permission denied for category creation: {request.user.email if request.user.is_authenticated else 'Guest'}")
            return Response({'error': 'Permission denied for category creation.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                category = serializer.save()
                logger.info(f"Category created: {category.name}, Admin: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error while creating category: {str(e)}", exc_info=True)
                return Response({'error': 'Error while creating category.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"Serializer error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, category_id=None):
        """
        Update categories, only by admins.
        """
        if not category_id:
            logger.error("Category ID not provided")
            return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"Permission denied for update: {request.user.email if request.user.is_authenticated else 'Guest'}, ID: {category_id}")
            return Response({'error': 'Permission denied for update.'}, status=status.HTTP_403_FORBIDDEN)

        logger.debug(f"Category update query received: {request.user.email}, ID: {category_id}")
        try:
            category = Category.objects.filter(id=category_id, is_deleted=False).first()
            if not category:
                logger.error(f"Category not found: ID {category_id}")
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Category updated: {category.name}, Admin: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error(f"Serializer error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error while updating category: {str(e)}", exc_info=True)
            return Response({'error': 'Error while updating category.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, category_id=None):
        """
        Only admins can delete categories.
        """
        if not category_id:
            logger.error("Category ID not provided")
            return Response({'error': 'Category ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"Permission denied for category deletion: {request.user.email if request.user.is_authenticated else 'Guest'}, ID: {category_id}")
            return Response({'error': 'Permission denied for category deletion: only admins can delete.'}, status=status.HTTP_403_FORBIDDEN)

        logger.debug(f"Category delete query received: {request.user.email}, ID: {category_id}")
        try:
            category = Category.objects.filter(id=category_id, is_deleted=False).first()
            if not category:
                logger.error(f"Category not found: ID {category_id}")
                return Response({'error': 'Category not found!'}, status=status.HTTP_404_NOT_FOUND)

            category.is_deleted = True
            category.save()
            logger.info(f"Category deleted: {category.name}, Admin: {request.user.email}")
            return Response({'message': 'Category successfully deleted.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error while deleting category: {str(e)}", exc_info=True)
            return Response({'error': 'Error while deleting category.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MenuItemView(APIView):
    def get(self, request, item_id=None):
        # Menu can be viewed by everyone
        
        logger.debug(f"Menu item query received: {request.user.email if request.user.is_authenticated else 'Guest'}, ID: {item_id}")
        try:
            if item_id:
                item = MenuItem.objects.filter(id=item_id, is_deleted=False).first()
                if not item:
                    logger.error(f"Menu item not found: ID {item_id}")
                    return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
                serializer = MenuItemSerializer(item)
                logger.info(f"Menu item details returned: ID {item_id}")
                return Response(serializer.data, status=status.HTTP_200_OK)

            items = MenuItem.objects.filter(is_deleted=False)
            serializer = MenuItemSerializer(items, many=True)
            logger.info(f"Menu item list returned: count: {items.count()}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error while retrieving item list: {str(e)}", exc_info=True)
            return Response({'error': 'Error while retrieving item list'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        Create a menu item, only for admins.
        """
        logger.debug(f"Menu item creation query received: {request.data}")
        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"Menu creation is restricted to admins: {request.user.email if request.user.is_authenticated else 'Guest'}")
            return Response({'error': 'Only admins can create menu items'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            try:
                item = serializer.save()
                logger.info(f"Menu item created: {item.name}, Admin: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error while creating menu item: {str(e)}", exc_info=True)
                return Response({'error': 'Error while creating menu item.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"Serializer error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, item_id=None):
        """
        Update menu item, only for admins.
        """
        if not item_id:
            logger.error("Menu item ID not provided.")
            return Response({'error': 'Menu item ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"Unauthorized menu item modification: {request.user.email if request.user.is_authenticated else 'Guest'}, ID: {item_id}")
            return Response({'error': 'Unauthorized menu item modification, only admins can modify.'}, status=status.HTTP_403_FORBIDDEN)

        logger.debug(f"Menu item update query received: {request.user.email}, ID: {item_id}")
        try:
            item = MenuItem.objects.filter(id=item_id, is_deleted=False).first()
            if not item:
                logger.error(f"Menu item not found: ID {item_id}")
                return Response({'error': 'Menu item not found.'}, status=status.HTTP_404_NOT_FOUND)

            serializer = MenuItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Menu item updated: {item.name}, Admin: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error(f"Serializer error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error while updating menu item: {str(e)}", exc_info=True)
            return Response({'error': 'Error while updating menu item.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, item_id=None):
        """
        Only admins can delete menu items.
        """
        if not item_id:
            logger.error("Menu item ID not provided")
            return Response({'error': 'Menu item ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"Unauthorized menu deletion attempt: {request.user.email if request.user.is_authenticated else 'Guest'}, ID: {item_id}")
            return Response({'error': 'Only admins can delete menu items'}, status=status.HTTP_403_FORBIDDEN)

        logger.debug(f"Admin delete item query received: {request.user.email}, ID: {item_id}")
        try:
            item = MenuItem.objects.filter(id=item_id, is_deleted=False).first()
            if not item:
                logger.error(f"Menu item not found: ID {item_id}")
                return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)

            item.is_deleted = True
            item.save()
            logger.info(f"Menu item deleted: {item.name}, Admin: {request.user.email}")
            return Response({'message': 'Menu item successfully deleted.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error while deleting menu item: {str(e)}", exc_info=True)
            return Response({'error': 'Error while deleting menu item.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

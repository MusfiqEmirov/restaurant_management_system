from rest_framework import serializers

from .models import *
from project_apps.core.constants import DISCOUNT_PERCENTAGES


# Serializer for Category model
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
        # These fields are read-only and cannot be modified
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
    
    # Custom validation for the 'name' field
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Category name cannot be empty")
        return value
    

# Serializer for MenuItem model
class MenuItemSerializer(serializers.ModelSerializer):
    # Nested serializer to display the category's details
    category = CategorySerializer(read_only=True)
    # Allow setting the category via its ID, while not exposing it as a read-only field
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_deleted=False),
        source="category",
        write_only=True
    )
    # Add the discounted price, calculated by the 'get_discounted_price' method in MenuItem model
    discounted_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2, 
        read_only=True, 
        source="get_discounted_price"
    )
    
    # Yeni təhlükəsiz sahələr
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField() 
    
    class Meta:
        model = MenuItem
        fields = [
            "id",
            "category",
            "category_id",
            "name",
            "description",
            "price",
            "image",
            "thumbnail",
            "is_available",
            "discount_percentage",
            "discounted_price",
            "created_at",
            "updated_at",
            "is_deleted"
        ]

    # Custom validation for the 'price' field
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value
    
    # Custom validation for the 'discount_percentage' field
    def validate_discount_percentage(self, value):
        valid_discounts = [choice[0] for choice in DISCOUNT_PERCENTAGES]
        if value not in valid_discounts:
            raise serializers.ValidationError("Invalid discount percentage")
        return value

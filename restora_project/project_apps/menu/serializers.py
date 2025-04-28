from rest_framework import serializers

from .models import *
from project_apps.core.constants import DISCOUNT_PERCENTAGES


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
         # ancaq oxuna biler deyiwdirile bilmez
        read_only_fields = [ 
            "id",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
    
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("categpriya bow ola bilmez")
        return value
    

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_deleted=False),
        source="category",
        write_only=True
        )
    discounted_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2, 
        read_only=True, 
        source="get_discounted_price"
        )
    
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

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("qiymet musbet olmalidir")
        return value
    
    def validate_discount_percentage(self, value):
        valid_discounts = [choice[0] for choice in DISCOUNT_PERCENTAGES]
        if value not in valid_discounts:
            raise serializers.ValidationError("endirim faizi yalniwdir")
        return value


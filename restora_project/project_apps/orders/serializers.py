from rest_framework import serializers
from django.db.models import Sum

from .models import Order, OrderItem
from project_apps.accounts.models import User
from project_apps.accounts.serializers import UserSerializer
from project_apps.menu.serializers import MenuItemSerializer
from project_apps.menu.models import MenuItem
from project_apps.core.constants import STATUS_CHOICES, PAYMENT_TYPE_CHOICES


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.filter(is_available=True, is_deleted=False),
        source="menu_item",
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menu_item",
            "menu_item_id",
            "quantity",
            "price",
            "created_at",
            "updated_at",
            "is_deleted",
        ]
         # ancaq oxuna biler deyiwdirile bilmez
        read_only_fields = [ 
            "id",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("say hemiwe musbet olmalidir")
        return value
    

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False, role="customer"),
        source="user",
        write_only=True
    )
    order_items = OrderItemSerializer(many=True)
    bonus_points = serializers.IntegerField(
        source="calculate_bonus_points", 
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_id",
            "total_amount",
            "status",
            "payment_type",
            "order_items",
            "bonus_points",
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
    
    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError("yalniw status deyeri")
        return value

    def validate_payment_type(self, value):
        valid_payment_types = [choice[0] for choice in PAYMENT_TYPE_CHOICES]
        if value not in valid_payment_types:
            raise serializers.ValidationError("yalniw odenis novu daxil etdiniz")
        return value
    

class SalesReportSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    payment_type = serializers.ChoiceField(choices=PAYMENT_TYPE_CHOICES, required=False)
    orders = OrderSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    order_count = serializers.IntegerField(read_only=True)
    total_bonus_points = serializers.IntegerField(read_only=True)

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("bawlangic tariwi bitiw tarixinnen boyuk ola bilmez")
        return data

    

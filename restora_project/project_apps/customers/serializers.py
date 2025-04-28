from rest_framework import serializers

from .models import *
from project_apps.accounts.serializers import UserSerializer
from project_apps.accounts.models import User
from project_apps.orders.serializers import OrderSerializer
from project_apps.orders.models import Order


class BonusTransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False, role="customer"),
        source="user",
        write_only=True
    )
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.filter(is_deleted=False),
        source="order",
        write_only=True,
        required=False
    )

    class Meta:
        model = BonusTransaction
        fields = [
            "id",
            "user",
            "user_id",
            "points",
            "description",
            "order",
            "order_id",
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

        def validate_points(self, value):
            if value == 0:
                raise serializers.ValidationError("Xallar sifir ola bilmez")
            return value

        def validate_description(self, value):
            if not value.strip():
                raise serializers.ValidationError("tesvir bow olmamalidir")
            return value
